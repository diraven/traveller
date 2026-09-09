import { PermissionFlagsBits } from "discord.js";
import { describe, expect, it } from "vitest";

import {
	BAN_BUTTON_ID,
	type Ban,
	banCommandText,
	banEmbed,
	embedField,
	embedReason,
	fanOut,
	NO_REASON,
	REASON_FIELD,
	TARGET_ID_FIELD,
} from "../src/handlers/bans_sharing/share.ts";
import {
	asClient,
	asUser,
	fakeChannel,
	fakeClient,
	fakeDb,
	fakeGuild,
	fakeUser,
	firstArg,
} from "./fakes.ts";

function ban(reason?: string): Ban {
	return {
		guildId: "origin",
		guildName: "Origin",
		actor: asUser(fakeUser({ id: "10", username: "mod" })),
		target: asUser(fakeUser({ id: "20", username: "troll" })),
		reason,
	};
}

describe("banEmbed", () => {
	it("carries the ids the buttons read back", () => {
		const embed = banEmbed(ban("spam"));
		expect(embedField(embed, TARGET_ID_FIELD)).toBe("20");
		expect(embedField(embed, "actor_id")).toBe("10");
		expect(embedField(embed, "guild_id")).toBe("origin");
		expect(embedField(embed, REASON_FIELD)).toBe("spam");
	});

	it("stands in for an empty reason, since embed values cannot be empty", () => {
		const embed = banEmbed(ban(undefined));
		expect(embedField(embed, REASON_FIELD)).toBe(NO_REASON);
		expect(embedReason(embed)).toBeUndefined();
	});
});

describe("banCommandText", () => {
	it("leaves delete_messages empty and appends the reason", () => {
		expect(banCommandText("20", "spam")).toBe(
			"/ban user:20 delete_messages: reason: spam",
		);
		expect(banCommandText("20", undefined)).toBe(
			"/ban user:20 delete_messages:",
		);
	});
});

describe("fanOut", () => {
	it("posts the notice and the copy-pasteable command to each server", async () => {
		const channel = fakeChannel("chanA");
		const guild = fakeGuild({
			id: "guildA",
			channel,
			mePermissions: [PermissionFlagsBits.BanMembers],
		});
		const db = fakeDb([
			{
				match: "AS channel_id",
				rows: [{ guild_id: "guildA", channel_id: "chanA" }],
			},
			{ match: "SELECT 1 FROM bans_sharing_trusted_moderators", rowCount: 0 },
		]);

		const result = await fanOut(
			asClient(fakeClient([], [guild])),
			db,
			ban("spam"),
		);

		expect(result).toEqual({ delivered: 1, total: 1 });
		const payload = firstArg<{
			components?: unknown[];
			embeds: { title: string }[];
		}>(channel.send);
		expect(payload.embeds[0]?.title).toBe("Новий бан на іншому сервері");
		expect(JSON.stringify(payload.components)).toContain(BAN_BUTTON_ID);
	});

	it("bans automatically when the actor is trusted there", async () => {
		const channel = fakeChannel("chanA");
		const guild = fakeGuild({
			id: "guildA",
			channel,
			mePermissions: [PermissionFlagsBits.BanMembers],
		});
		const db = fakeDb([
			{
				match: "AS channel_id",
				rows: [{ guild_id: "guildA", channel_id: "chanA" }],
			},
			{
				match: "SELECT 1 FROM bans_sharing_trusted_moderators",
				rows: [{ ok: 1 }],
			},
		]);

		await fanOut(asClient(fakeClient([], [guild])), db, ban("spam"));

		expect(guild.bans.create).toHaveBeenCalledWith("20", { reason: "spam" });
		const payload = firstArg<{ embeds: { description?: string }[] }>(
			channel.send,
		);
		expect(payload.embeds[0]?.description).toContain("застосовано автоматично");
		// No follow-up command message: there is nothing left to do by hand.
		expect(channel.send).toHaveBeenCalledTimes(1);
	});

	it("omits buttons where the bot cannot ban", async () => {
		const channel = fakeChannel("chanA");
		const guild = fakeGuild({ id: "guildA", channel, mePermissions: [] });
		const db = fakeDb([
			{
				match: "AS channel_id",
				rows: [{ guild_id: "guildA", channel_id: "chanA" }],
			},
		]);

		await fanOut(asClient(fakeClient([], [guild])), db, ban("spam"));

		const payload = firstArg<{
			components?: unknown[];
			embeds: { footer?: { text: string } }[];
		}>(channel.send);
		expect(payload.components).toBeUndefined();
		expect(payload.embeds[0]?.footer?.text).toContain("відсутні права на бан");
	});

	it("keeps going when one server fails", async () => {
		const good = fakeGuild({
			id: "guildB",
			channel: fakeChannel("chanB"),
			mePermissions: [PermissionFlagsBits.BanMembers],
		});
		const db = fakeDb([
			{
				match: "AS channel_id",
				rows: [
					{ guild_id: "missing", channel_id: "chanX" },
					{ guild_id: "guildB", channel_id: "chanB" },
				],
			},
			{ match: "SELECT 1 FROM bans_sharing_trusted_moderators", rowCount: 0 },
		]);

		const result = await fanOut(
			asClient(fakeClient([], [good])),
			db,
			ban("spam"),
		);

		expect(result).toEqual({ delivered: 1, total: 2 });
	});
});
