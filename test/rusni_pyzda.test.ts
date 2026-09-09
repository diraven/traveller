import { afterEach, describe, expect, it, vi } from "vitest";

import { Color } from "../src/discord.ts";
import { fetchLosses, rusniPyzda } from "../src/handlers/rusni_pyzda.ts";
import { asCommand, fakeInteraction, firstArg } from "./fakes.ts";

const PAYLOAD = {
	data: {
		date: "2026-09-07",
		day: 1657,
		resource: "https://russianwarship.rip/",
		stats: { tanks: 100, aircraft: 5 },
		increase: { tanks: 3 },
	},
};

function mockFetch(payload: unknown): void {
	vi.stubGlobal(
		"fetch",
		vi.fn(async () => new Response(JSON.stringify(payload))),
	);
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe("fetchLosses", () => {
	it("asks for the latest statistics rather than a given date", async () => {
		mockFetch(PAYLOAD);
		await fetchLosses();
		expect(vi.mocked(fetch).mock.calls[0]?.[0]).toContain("/statistics/latest");
	});

	it("renders each stat with its increase", async () => {
		mockFetch(PAYLOAD);
		const embed = await fetchLosses();

		expect(embed.title).toBe("Втрати ворога");
		expect(embed.fields).toEqual([
			{ name: "tanks", value: "100 (+3)", inline: true },
			// Missing from `increase`, so it falls back to zero.
			{ name: "aircraft", value: "5 (+0)", inline: true },
		]);
		expect(embed.footer?.text).toContain("1657й день війни");
	});

	it("reports upstream errors instead of throwing", async () => {
		mockFetch({ errors: {}, message: "Boom." });
		const embed = await fetchLosses();

		expect(embed.title).toBe("Втрати ворога: помилка");
		expect(embed.description).toBe("Boom.");
		expect(embed.color).toBe(Color.red);
	});
});

describe("rusniPyzda", () => {
	it("defers before the slow call and edits afterwards", async () => {
		mockFetch(PAYLOAD);
		const interaction = fakeInteraction();
		await rusniPyzda(asCommand(interaction), { db: {} as never });

		expect(interaction.deferReply).toHaveBeenCalled();
		expect(interaction.reply).not.toHaveBeenCalled();
		const payload = firstArg<{ embeds: { title: string }[] }>(
			interaction.editReply,
		);
		expect(payload.embeds[0]?.title).toBe("Втрати ворога");
	});
});
