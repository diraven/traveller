import { AuditLogEvent, PermissionFlagsBits } from "discord.js";
import { describe, expect, it } from "vitest";

import {
	noShareButton,
	onAuditLogEntry,
	promptToShare,
	SHARE_BUTTON_ID,
	shareButton,
} from "../src/handlers/bans_sharing/confirm.ts";
import { banEmbed } from "../src/handlers/bans_sharing/share.ts";
import {
	asButton,
	asClient,
	asGuild,
	asUser,
	fakeButtonInteraction,
	fakeChannel,
	fakeClient,
	fakeDb,
	fakeGuild,
	fakeUser,
	firstArg,
	firstEmbed,
} from "./fakes.ts";

const ACTOR = fakeUser({ id: "10", username: "mod" });
const TARGET = fakeUser({ id: "20", username: "troll" });

function ban(guildId = "origin") {
	return {
		guildId,
		guildName: "Origin",
		actor: asUser(ACTOR),
		target: asUser(TARGET),
		reason: "spam",
	};
}

function guildRow(channelId: string | null) {
	return {
		match: "AS id",
		rows: [
			{
				id: "origin",
				bans_sharing_channel_id: channelId,
				verification_role_id: null,
			},
		],
	};
}

/** The claim insert either wins (1) or loses to another server (0). */
function claim(won: boolean) {
	return { match: "INSERT INTO bans_sharing_bans", rowCount: won ? 1 : 0 };
}

describe("promptToShare", () => {
	it("skips a ban another server already claimed", async () => {
		const channel = fakeChannel("chan1");
		const guild = fakeGuild({ id: "origin", channel });
		const db = fakeDb([guildRow("chan1"), claim(false)]);

		await promptToShare(asClient(fakeClient([], [guild])), db, ban());

		expect(channel.send).not.toHaveBeenCalled();
	});

	it("claims nothing when the server has no notification channel", async () => {
		const channel = fakeChannel();
		const guild = fakeGuild({ id: "origin", channel });
		const db = fakeDb([guildRow(null), claim(true)]);

		await promptToShare(asClient(fakeClient([], [guild])), db, ban());

		expect(channel.send).not.toHaveBeenCalled();
		// Another server banning the same user must still get its own prompt.
		expect(
			db.queries.some((q) => q.sql.includes("INSERT INTO bans_sharing_bans")),
		).toBe(false);
	});

	it("asks the origin server to confirm, and claims the ban", async () => {
		const channel = fakeChannel("chan1");
		const guild = fakeGuild({ id: "origin", channel });
		const db = fakeDb([guildRow("chan1"), claim(true)]);

		await promptToShare(asClient(fakeClient([], [guild])), db, ban());

		const payload = firstArg<{
			embeds: { title: string }[];
			components: unknown[];
		}>(channel.send);
		expect(payload.embeds[0]?.title).toBe("Новий бан на цьому сервері");
		expect(JSON.stringify(payload.components)).toContain(SHARE_BUTTON_ID);

		// The copy-pasteable command comes as a reply to the prompt.
		const reply = firstArg<{ content: string }>(channel.message.reply);
		expect(reply.content).toContain("/ban user:20");

		expect(
			db.queries.find((q) => q.sql.includes("INSERT INTO bans_sharing_bans"))
				?.values,
		).toEqual(["20", "spam", "10"]);
	});

	// The regression that motivated the claim/release split: recording the ban
	// before the notice went up meant a channel the bot could see but not post
	// in silently swallowed the ban for the entire network, forever.
	it("releases the claim when the notice cannot be posted", async () => {
		const channel = fakeChannel("chan1", { sendFails: true });
		const guild = fakeGuild({ id: "origin", channel });
		const db = fakeDb([guildRow("chan1"), claim(true)]);

		await expect(
			promptToShare(asClient(fakeClient([], [guild])), db, ban()),
		).rejects.toThrow();

		expect(
			db.queries.some((q) => q.sql.includes("DELETE FROM bans_sharing_bans")),
		).toBe(true);
	});

	// The notice is what matters; the follow-up command is a convenience.
	it("keeps the claim when only the follow-up command fails", async () => {
		const channel = fakeChannel("chan1");
		channel.message.reply.mockRejectedValueOnce(new Error("no history"));
		const guild = fakeGuild({ id: "origin", channel });
		const db = fakeDb([guildRow("chan1"), claim(true)]);

		await promptToShare(asClient(fakeClient([], [guild])), db, ban());

		expect(
			db.queries.some((q) => q.sql.includes("DELETE FROM bans_sharing_bans")),
		).toBe(false);
	});

	it("fails loudly when the notification channel has been deleted", async () => {
		// channels.fetch throws for a missing channel; it never resolves to null.
		const guild = fakeGuild({ id: "origin", channel: fakeChannel("gone") });
		const db = fakeDb([guildRow("chan1"), claim(true)]);

		await expect(
			promptToShare(asClient(fakeClient([], [guild])), db, ban()),
		).rejects.toThrow();

		// Nothing was claimed, so the ban is not lost.
		expect(
			db.queries.some((q) => q.sql.includes("INSERT INTO bans_sharing_bans")),
		).toBe(false);
	});
});

describe("onAuditLogEntry", () => {
	function entry(overrides: Record<string, unknown> = {}) {
		return {
			action: AuditLogEvent.MemberBanAdd,
			executorId: "10",
			targetId: "20",
			reason: "spam",
			...overrides,
		};
	}

	it("ignores audit log entries that are not bans", async () => {
		const client = fakeClient([ACTOR, TARGET], []);
		const db = fakeDb([]);

		await onAuditLogEntry(asClient(client), db)(
			entry({ action: AuditLogEvent.MemberKick }) as never,
			asGuild(fakeGuild({ id: "origin" })),
		);

		expect(client.users.fetch).not.toHaveBeenCalled();
	});

	it("ignores bans the bot itself applied, which are echoes of a share", async () => {
		const client = fakeClient([ACTOR, TARGET], []);
		const db = fakeDb([]);

		await onAuditLogEntry(asClient(client), db)(
			entry({ executorId: "bot" }) as never,
			asGuild(fakeGuild({ id: "origin" })),
		);

		expect(client.users.fetch).not.toHaveBeenCalled();
	});

	it("prompts for a moderator's ban", async () => {
		const channel = fakeChannel("chan1");
		const guild = fakeGuild({ id: "origin", channel });
		const client = fakeClient([ACTOR, TARGET], [guild]);
		const db = fakeDb([guildRow("chan1"), claim(true)]);

		await onAuditLogEntry(asClient(client), db)(
			entry() as never,
			asGuild(guild),
		);

		expect(firstEmbed(channel.send)?.title).toBe("Новий бан на цьому сервері");
	});
});

describe("confirm buttons", () => {
	const embed = banEmbed(ban());

	it("refuses a click without Ban Members", async () => {
		const interaction = fakeButtonInteraction({ permissions: [], embed });
		await shareButton(asButton(interaction), { db: fakeDb([]) });

		expect(interaction.update).not.toHaveBeenCalled();
		expect(firstEmbed(interaction.reply)?.description).toBe(
			"Відсутній доступ.",
		);
	});

	// Discord leaves stale buttons clickable, so an answered prompt has to
	// refuse rather than fan out a second time.
	it("refuses a prompt that already carries a status", async () => {
		const answered = { ...embed, description: "**Статус:** проігноровано" };
		const interaction = fakeButtonInteraction({
			permissions: [PermissionFlagsBits.BanMembers],
			embed: answered,
			client: fakeClient([ACTOR, TARGET], []),
		});
		const db = fakeDb([{ match: "AS channel_id", rows: [] }]);

		await shareButton(asButton(interaction), { db });

		expect(interaction.update).not.toHaveBeenCalled();
		expect(firstEmbed(interaction.reply)?.description).toBe(
			"Цей бан вже опрацьовано.",
		);
	});

	it("acknowledges before resolving users, so the click cannot time out", async () => {
		const guild = fakeGuild({ id: "origin" });
		// A cold cache, which is exactly the case after a restart.
		const client = fakeClient([], []);
		const interaction = fakeButtonInteraction({
			permissions: [PermissionFlagsBits.BanMembers],
			guild,
			embed,
			client,
		});
		const db = fakeDb([{ match: "AS channel_id", rows: [] }]);

		await shareButton(asButton(interaction), { db });

		// The ack came first; the failed lookup is reported by editing after it.
		expect(interaction.update).toHaveBeenCalled();
		expect(firstEmbed(interaction.editReply)?.description).toContain(
			"дані бану неповні",
		);
	});

	it("fans out and reports how many servers were reached", async () => {
		const guild = fakeGuild({ id: "origin" });
		const interaction = fakeButtonInteraction({
			permissions: [PermissionFlagsBits.BanMembers],
			guild,
			embed,
			user: fakeUser({ id: "2" }),
			client: fakeClient([ACTOR, TARGET], []),
		});
		const db = fakeDb([{ match: "AS channel_id", rows: [] }]);

		await shareButton(asButton(interaction), { db });

		expect(firstEmbed(interaction.update)?.description).toContain(
			"поширюється",
		);
		expect(firstEmbed(interaction.editReply)?.description).toContain(
			"поширено на 0 з 0 серверів",
		);
	});

	// The claim was taken when the prompt went up, so a fan-out that never ran
	// has to give it back - otherwise the ban is marked handled network-wide
	// with nobody notified, and the prompt sits at "поширюється" forever.
	it("releases the claim when the fan-out cannot even start", async () => {
		const interaction = fakeButtonInteraction({
			permissions: [PermissionFlagsBits.BanMembers],
			guild: fakeGuild({ id: "origin" }),
			embed,
			client: fakeClient([ACTOR, TARGET], []),
		});
		const db = fakeDb([
			{ match: "AS channel_id", error: new Error("connection terminated") },
		]);

		await expect(shareButton(asButton(interaction), { db })).rejects.toThrow(
			"connection terminated",
		);

		expect(firstEmbed(interaction.editReply)?.description).toContain(
			"не вдалося поширити",
		);
		expect(
			db.queries.some((q) => q.sql.includes("DELETE FROM bans_sharing_bans")),
		).toBe(true);
	});

	it("marks the prompt ignored", async () => {
		const interaction = fakeButtonInteraction({
			permissions: [PermissionFlagsBits.BanMembers],
			embed,
			user: fakeUser({ id: "3" }),
		});
		await noShareButton(asButton(interaction), { db: fakeDb([]) });

		const payload = firstArg<{
			embeds: { description: string }[];
			components: { components: { disabled: boolean }[] }[];
		}>(interaction.update);
		expect(payload.embeds[0]?.description).toContain("проігноровано");
		expect(
			payload.components[0]?.components.every((button) => button.disabled),
		).toBe(true);
	});
});
