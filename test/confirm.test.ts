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

function firstEmbed(mock: { mock: { calls: unknown[][] } }) {
	const [payload] = mock.mock.calls[0] as [
		{ embeds: { title?: string; description?: string }[] },
	];
	return payload.embeds[0];
}

describe("promptToShare", () => {
	it("skips a ban that has already been seen anywhere", async () => {
		const channel = fakeChannel();
		const guild = fakeGuild({ id: "origin", channel });
		const db = fakeDb([
			{ match: "SELECT 1 FROM bans_sharing_bans", rows: [{ ok: 1 }] },
		]);

		await promptToShare(asClient(fakeClient([], [guild])), db, ban());

		expect(channel.send).not.toHaveBeenCalled();
	});

	it("records nothing when the server has no notification channel", async () => {
		const channel = fakeChannel();
		const guild = fakeGuild({ id: "origin", channel });
		const db = fakeDb([
			{ match: "SELECT 1 FROM bans_sharing_bans", rowCount: 0 },
			guildRow(null),
		]);

		await promptToShare(asClient(fakeClient([], [guild])), db, ban());

		expect(channel.send).not.toHaveBeenCalled();
		// Another server banning the same user must still get its own prompt.
		expect(
			db.queries.some((q) => q.sql.includes("INSERT INTO bans_sharing_bans")),
		).toBe(false);
	});

	it("asks the origin server to confirm, and marks the ban seen", async () => {
		const channel = fakeChannel("chan1");
		const guild = fakeGuild({ id: "origin", channel });
		const db = fakeDb([
			{ match: "SELECT 1 FROM bans_sharing_bans", rowCount: 0 },
			guildRow("chan1"),
		]);

		await promptToShare(asClient(fakeClient([], [guild])), db, ban());

		const [payload] = channel.send.mock.calls[0] as [
			{ embeds: { title: string }[]; components: unknown[] },
		];
		expect(payload.embeds[0]?.title).toBe("Новий бан на цьому сервері");
		expect(JSON.stringify(payload.components)).toContain(SHARE_BUTTON_ID);

		// The copy-pasteable command comes as a reply to the prompt.
		const [reply] = channel.message.reply.mock.calls[0] as [
			{ content: string },
		];
		expect(reply.content).toContain("/ban user:20");

		expect(
			db.queries.find((q) => q.sql.includes("INSERT INTO bans_sharing_bans"))
				?.values,
		).toEqual(["20", "spam", "10"]);
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
		const db = fakeDb([
			{ match: "SELECT 1 FROM bans_sharing_bans", rowCount: 0 },
			guildRow("chan1"),
		]);

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

	it("marks the prompt ignored", async () => {
		const interaction = fakeButtonInteraction({
			permissions: [PermissionFlagsBits.BanMembers],
			embed,
			user: fakeUser({ id: "3" }),
		});
		await noShareButton(asButton(interaction), { db: fakeDb([]) });

		const [payload] = interaction.update.mock.calls[0] as [
			{
				embeds: { description: string }[];
				components: { components: { disabled: boolean }[] }[];
			},
		];
		expect(payload.embeds[0]?.description).toContain("проігноровано");
		expect(
			payload.components[0]?.components.every((button) => button.disabled),
		).toBe(true);
	});
});
