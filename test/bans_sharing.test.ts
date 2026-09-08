import { MessageFlags, PermissionFlagsBits } from "discord.js";
import { describe, expect, it } from "vitest";

import {
	banButton,
	bansSharing,
	skipButton,
} from "../src/handlers/bans_sharing/index.ts";
import {
	banEmbed,
	NO_REASON,
	REASON_FIELD,
} from "../src/handlers/bans_sharing/share.ts";
import {
	asButton,
	asCommand,
	asUser,
	fakeButtonInteraction,
	fakeChannel,
	fakeClient,
	fakeDb,
	fakeGuild,
	fakeInteraction,
	fakeUser,
} from "./fakes.ts";

const BAN_MEMBERS = [PermissionFlagsBits.BanMembers];
const TARGET = fakeUser({ id: "20", username: "troll" });

function guildRow(channelId: string | null) {
	return {
		match: "AS id",
		rows: [
			{
				id: "guild1",
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

describe("bans_sharing share", () => {
	it("refuses without Ban Members", async () => {
		const interaction = fakeInteraction({
			subcommand: "share",
			permissions: [],
			users: { user: TARGET },
		});
		const db = fakeDb([]);
		await bansSharing(asCommand(interaction), { db });

		expect(firstEmbed(interaction.reply)?.description).toBe(
			"Відсутній доступ.",
		);
		expect(db.queries).toHaveLength(0);
	});

	it("asks for a notification channel first", async () => {
		const interaction = fakeInteraction({
			subcommand: "share",
			permissions: BAN_MEMBERS,
			users: { user: TARGET },
		});
		await bansSharing(asCommand(interaction), { db: fakeDb([guildRow(null)]) });

		const [payload] = interaction.reply.mock.calls[0] as [{ flags: number }];
		expect(payload.flags).toBe(MessageFlags.Ephemeral);
		expect(firstEmbed(interaction.reply)?.title).toBe(
			"Не налаштовано канал сповіщень.",
		);
	});

	it("refuses a ban that was already shared", async () => {
		const interaction = fakeInteraction({
			subcommand: "share",
			permissions: BAN_MEMBERS,
			users: { user: TARGET },
		});
		const db = fakeDb([
			guildRow("chan1"),
			{ match: "SELECT 1 FROM bans_sharing_bans", rows: [{ ok: 1 }] },
		]);
		await bansSharing(asCommand(interaction), { db });

		expect(firstEmbed(interaction.reply)?.title).toBe("Бан вже поширено");
		expect(interaction.deferReply).not.toHaveBeenCalled();
	});

	it("checks the user really is banned before telling anyone", async () => {
		const interaction = fakeInteraction({
			subcommand: "share",
			permissions: BAN_MEMBERS,
			users: { user: TARGET },
			guild: fakeGuild({ bans: [] }),
		});
		const db = fakeDb([
			guildRow("chan1"),
			{ match: "SELECT 1 FROM bans_sharing_bans", rowCount: 0 },
		]);
		await bansSharing(asCommand(interaction), { db });

		expect(interaction.deferReply).toHaveBeenCalled();
		expect(firstEmbed(interaction.editReply)?.title).toBe(
			"Користувача не забанено",
		);
		// Nothing recorded, so the ban can still be shared once it is real.
		expect(
			db.queries.some((q) => q.sql.includes("INSERT INTO bans_sharing_bans")),
		).toBe(false);
	});

	it("records the ban and posts a local notice after fanning out", async () => {
		const channel = fakeChannel("chan1");
		const interaction = fakeInteraction({
			subcommand: "share",
			permissions: BAN_MEMBERS,
			users: { user: TARGET },
			strings: { reason: "spam" },
			user: fakeUser({ id: "1" }),
			guild: fakeGuild({ channel, bans: ["20"] }),
			client: fakeClient(),
		});
		const db = fakeDb([
			guildRow("chan1"),
			{ match: "SELECT 1 FROM bans_sharing_bans", rowCount: 0 },
			{ match: "AS channel_id", rows: [] },
		]);
		await bansSharing(asCommand(interaction), { db });

		const recorded = db.queries.find((q) =>
			q.sql.includes("INSERT INTO bans_sharing_bans"),
		);
		expect(recorded?.values).toEqual(["20", "spam", "1"]);
		expect(firstEmbed(channel.send)?.title).toBe("Новий бан на цьому сервері");
		expect(firstEmbed(interaction.editReply)?.title).toBe("Бан поширено");
	});
});

describe("bans_sharing trusted moderators", () => {
	it("resolves a moderator who is not a member of this server", async () => {
		const outsider = fakeUser({ id: "999", displayName: "Outsider" });
		const interaction = fakeInteraction({
			subcommand: "add_trusted_moderator",
			permissions: BAN_MEMBERS,
			strings: { user_id: "999" },
			user: fakeUser({ id: "1" }),
			client: fakeClient([outsider]),
		});
		const db = fakeDb([
			{ match: "INSERT INTO bans_sharing_trusted_moderators", rowCount: 1 },
		]);
		await bansSharing(asCommand(interaction), { db });

		expect(db.queries[0]?.values).toEqual(["1", "guild1", "999", "Outsider"]);
		expect(firstEmbed(interaction.reply)?.title).toBe("Успішно");
	});

	it("reports an unknown snowflake", async () => {
		const interaction = fakeInteraction({
			subcommand: "add_trusted_moderator",
			permissions: BAN_MEMBERS,
			strings: { user_id: "404" },
			client: fakeClient([]),
		});
		await bansSharing(asCommand(interaction), { db: fakeDb([]) });

		expect(firstEmbed(interaction.reply)?.title).toBe(
			"Користувача не знайдено",
		);
	});

	it("reports a duplicate", async () => {
		const outsider = fakeUser({ id: "999", displayName: "Outsider" });
		const interaction = fakeInteraction({
			subcommand: "add_trusted_moderator",
			permissions: BAN_MEMBERS,
			strings: { user_id: "999" },
			client: fakeClient([outsider]),
		});
		const db = fakeDb([
			{ match: "INSERT INTO bans_sharing_trusted_moderators", rowCount: 0 },
		]);
		await bansSharing(asCommand(interaction), { db });

		expect(firstEmbed(interaction.reply)?.description).toContain(
			"вже є довіреним модератором",
		);
	});

	it("removes by snowflake", async () => {
		const interaction = fakeInteraction({
			subcommand: "remove_trusted_moderator",
			permissions: BAN_MEMBERS,
			strings: { user_id: "999" },
		});
		const db = fakeDb([
			{
				match: "DELETE FROM bans_sharing_trusted_moderators",
				rows: [{ user_global_name: "Outsider" }],
			},
		]);
		await bansSharing(asCommand(interaction), { db });

		expect(firstEmbed(interaction.reply)?.description).toContain("Outsider");
	});
});

describe("bans_sharing set_channel", () => {
	it("stores the channel only after a successful test message", async () => {
		const channel = fakeChannel("chan9");
		const interaction = fakeInteraction({
			subcommand: "set_channel",
			permissions: [PermissionFlagsBits.Administrator],
			channels: { channel: { id: "chan9" } },
			guild: fakeGuild({ channel }),
		});
		const db = fakeDb([]);
		await bansSharing(asCommand(interaction), { db });

		expect(channel.send).toHaveBeenCalled();
		expect(db.queries[0]?.values).toEqual(["guild1", "chan9"]);
	});

	it("stores nothing when the channel is unreachable", async () => {
		const channel = fakeChannel("chan9", false);
		const interaction = fakeInteraction({
			subcommand: "set_channel",
			permissions: [PermissionFlagsBits.Administrator],
			channels: { channel: { id: "chan9" } },
			guild: fakeGuild({ channel }),
		});
		const db = fakeDb([]);
		await bansSharing(asCommand(interaction), { db });

		expect(db.queries).toHaveLength(0);
		expect(firstEmbed(interaction.editReply)?.title).toBe("Відсутній доступ");
	});
});

describe("bans_sharing check_config", () => {
	it("reports a missing View Audit Log permission", async () => {
		const interaction = fakeInteraction({
			subcommand: "check_config",
			permissions: [PermissionFlagsBits.Administrator],
			guild: fakeGuild({ mePermissions: [] }),
		});
		await bansSharing(asCommand(interaction), {
			db: fakeDb([guildRow(null)]),
		});

		const embed = firstEmbed(interaction.editReply) as {
			fields: { name: string }[];
		};
		expect(embed.fields.map((field) => field.name)).toContain(
			"Відсутній дозвіл на перегляд Audit Log.",
		);
	});
});

describe("ban notice buttons", () => {
	const embed = banEmbed({
		guildId: "origin",
		guildName: "Origin",
		actor: asUser(fakeUser({ id: "10" })),
		target: asUser(TARGET),
		reason: "spam",
	});

	it("bans in the guild the button was clicked in, not the embed's", async () => {
		const guild = fakeGuild({ id: "clicked" });
		const interaction = fakeButtonInteraction({
			permissions: BAN_MEMBERS,
			guild,
			embed,
			user: fakeUser({ id: "2" }),
		});
		await banButton(asButton(interaction), { db: fakeDb([]) });

		expect(interaction.deferUpdate).toHaveBeenCalled();
		expect(guild.bans.create).toHaveBeenCalledWith("20", { reason: "spam" });
		expect(firstEmbed(interaction.editReply)?.description).toContain(
			"теж забанено",
		);
	});

	it("passes no reason through when the embed carries the stand-in", async () => {
		const guild = fakeGuild({ id: "clicked" });
		const withoutReason = {
			...embed,
			fields: (embed.fields ?? []).map((field) =>
				field.name === REASON_FIELD ? { ...field, value: NO_REASON } : field,
			),
		};
		const interaction = fakeButtonInteraction({
			permissions: BAN_MEMBERS,
			guild,
			embed: withoutReason,
		});
		await banButton(asButton(interaction), { db: fakeDb([]) });

		expect(guild.bans.create).toHaveBeenCalledWith("20", {});
	});

	it("refuses a click without Ban Members", async () => {
		const guild = fakeGuild({ id: "clicked" });
		const interaction = fakeButtonInteraction({
			permissions: [],
			guild,
			embed,
		});
		await banButton(asButton(interaction), { db: fakeDb([]) });

		expect(guild.bans.create).not.toHaveBeenCalled();
		expect(firstEmbed(interaction.reply)?.description).toBe(
			"Відсутній доступ.",
		);
	});

	it("marks the notice ignored and disables the buttons", async () => {
		const interaction = fakeButtonInteraction({
			permissions: BAN_MEMBERS,
			embed,
			user: fakeUser({ id: "3" }),
		});
		await skipButton(asButton(interaction), { db: fakeDb([]) });

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
