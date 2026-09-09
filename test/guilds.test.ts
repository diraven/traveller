import { describe, expect, it } from "vitest";

import { reconcileGuilds } from "../src/guilds.ts";
import { asClient, fakeClient, fakeDb, fakeGuild } from "./fakes.ts";

describe("reconcileGuilds", () => {
	it("stores the guilds the bot is in", async () => {
		const guild = fakeGuild({ id: "1", name: "First" });
		const db = fakeDb([{ match: "SELECT id_ AS id FROM guilds", rows: [] }]);

		await reconcileGuilds(asClient(fakeClient([], [guild])), db);

		expect(
			db.queries.find((q) => q.sql.includes("INSERT INTO guilds"))?.values,
		).toEqual(["1", "First"]);
	});

	// An outage leaves the guild cached with no data, so its name is undefined.
	// Writing that would blank a name the database already has.
	it("leaves a guild that is mid-outage alone", async () => {
		const guild = fakeGuild({ id: "1", available: false });
		const db = fakeDb([
			{ match: "SELECT id_ AS id FROM guilds", rows: [{ id: "1" }] },
		]);

		await reconcileGuilds(asClient(fakeClient([], [guild])), db);

		expect(db.queries.some((q) => q.sql.includes("INSERT INTO guilds"))).toBe(
			false,
		);
		// It is unavailable, not gone: PRIVACY.md's wipe must not fire.
		expect(db.queries.some((q) => q.sql.includes("DELETE FROM guilds"))).toBe(
			false,
		);
	});

	// PRIVACY.md promises records go away when a server removes the bot, and a
	// removal while the bot was offline is only visible by comparing at startup.
	it("wipes a guild that is no longer in the cache", async () => {
		const db = fakeDb([
			{ match: "SELECT id_ AS id FROM guilds", rows: [{ id: "gone" }] },
		]);

		await reconcileGuilds(asClient(fakeClient([], [])), db);

		expect(
			db.queries.find((q) => q.sql.includes("DELETE FROM guilds"))?.values,
		).toEqual(["gone"]);
	});
});
