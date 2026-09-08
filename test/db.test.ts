/**
 * Exercises the SQL against a real Postgres. Skipped unless TEST_DATABASE_URL
 * points at a throwaway database - CI provides one as a service container.
 *
 *   docker run --rm -e POSTGRES_PASSWORD=test -e POSTGRES_DB=traveller_test \
 *     -p 55432:5432 postgres:18-alpine
 *   TEST_DATABASE_URL=postgres://postgres:test@localhost:55432/traveller_test \
 *     pnpm test
 */
import process from "node:process";
import pg from "pg";
import { afterAll, beforeEach, describe, expect, it } from "vitest";

import * as db from "../src/db.ts";
import { migrate } from "../src/migrate.ts";

const url = process.env.TEST_DATABASE_URL;
const pool = url ? new pg.Pool({ connectionString: url }) : null;

afterAll(async () => {
	await pool?.end();
});

describe.skipIf(!pool)("database", () => {
	// Non-null throughout: the whole suite is skipped without a database.
	const conn = pool as pg.Pool;

	beforeEach(async () => {
		await migrate(conn);
		await conn.query(
			"TRUNCATE guilds, bans_sharing_bans, bans_sharing_trusted_moderators",
		);
	});

	it("applies migrations more than once without complaining", async () => {
		expect(await migrate(conn)).toEqual([]);
	});

	it("returns snowflakes as strings, not lossy numbers", async () => {
		const big = "1234567890123456789";
		await db.setBansSharingChannel(conn, big, big);
		const guild = await db.getGuild(conn, big);

		expect(guild?.id).toBe(big);
		expect(guild?.bans_sharing_channel_id).toBe(big);
	});

	it("upserts each guild setting without clobbering the other", async () => {
		await db.setBansSharingChannel(conn, "1", "3000");
		await db.setVerificationRole(conn, "1", "4000");

		expect(await db.getGuild(conn, "1")).toMatchObject({
			bans_sharing_channel_id: "3000",
			verification_role_id: "4000",
		});
	});

	it("lists sharing channels except the origin server", async () => {
		await db.setBansSharingChannel(conn, "1", "3001");
		await db.setBansSharingChannel(conn, "2", "3002");
		await db.setVerificationRole(conn, "3", "4000");

		expect(await db.listBansSharingChannels(conn, "1")).toEqual([
			{ guild_id: "2", channel_id: "3002" },
		]);
	});

	it("reports a duplicate trusted moderator instead of throwing", async () => {
		const row = {
			guild_id: "1",
			user_id: "2",
			user_global_name: "Mod",
			created_by: "3",
		};
		expect(await db.addTrustedModerator(conn, row)).toBe(true);
		expect(await db.addTrustedModerator(conn, row)).toBe(false);
		expect(await db.isTrustedModerator(conn, "1", "2")).toBe(true);
		expect(await db.isTrustedModerator(conn, "9", "2")).toBe(false);
	});

	it("returns the removed moderator, or null when there was none", async () => {
		await db.addTrustedModerator(conn, {
			guild_id: "1",
			user_id: "2",
			user_global_name: "Mod",
			created_by: "3",
		});

		expect(await db.removeTrustedModerator(conn, "1", "2")).toMatchObject({
			user_global_name: "Mod",
		});
		expect(await db.removeTrustedModerator(conn, "1", "2")).toBeNull();
	});

	it("lists trusted moderators for one guild only", async () => {
		await db.addTrustedModerator(conn, {
			guild_id: "1",
			user_id: "2",
			user_global_name: "Mod",
			created_by: "3",
		});
		await db.addTrustedModerator(conn, {
			guild_id: "9",
			user_id: "8",
			user_global_name: "Other",
			created_by: "3",
		});

		const listed = await db.listTrustedModerators(conn, "1");
		expect(listed.map((row) => row.user_id)).toEqual(["2"]);
	});

	it("records a ban once and remembers it", async () => {
		expect(await db.hasSeenBan(conn, "20")).toBe(false);
		await db.recordBan(conn, "20", "10", "spam");
		// A second ban of the same user must not blow up on the primary key.
		await db.recordBan(conn, "20", "11", undefined);

		expect(await db.hasSeenBan(conn, "20")).toBe(true);
		const { rows } = await conn.query(
			"SELECT reason, created_by FROM bans_sharing_bans WHERE id_ = $1",
			["20"],
		);
		expect(rows[0]).toEqual({ reason: "spam", created_by: "10" });
	});

	it("stores a null reason when there was none", async () => {
		await db.recordBan(conn, "21", "10", undefined);
		const { rows } = await conn.query(
			"SELECT reason FROM bans_sharing_bans WHERE id_ = $1",
			["21"],
		);
		expect(rows[0]?.reason).toBeNull();
	});

	it("removes a guild's trusted moderators along with the guild", async () => {
		await db.upsertGuild(conn, "1", "Server");
		await db.addTrustedModerator(conn, {
			guild_id: "1",
			user_id: "2",
			user_global_name: "Mod",
			created_by: "3",
		});

		await db.deleteGuild(conn, "1");

		expect(await db.getGuild(conn, "1")).toBeNull();
		expect(await db.listTrustedModerators(conn, "1")).toEqual([]);
	});

	it("keeps a guild's settings when its name changes", async () => {
		await db.setBansSharingChannel(conn, "1", "3000");
		await db.upsertGuild(conn, "1", "Renamed");

		expect(await db.getGuild(conn, "1")).toMatchObject({
			bans_sharing_channel_id: "3000",
		});
		expect(await db.listGuildIds(conn)).toEqual(["1"]);
	});
});
