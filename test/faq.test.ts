import { MessageFlags } from "discord.js";
import { describe, expect, it } from "vitest";

import { COMMANDS, FAQ_COMMAND } from "../src/commands.ts";
import { FAQ_ENTRIES } from "../src/faq_entries.ts";
import { faq } from "../src/handlers/faq.ts";
import { asCommand, fakeInteraction, firstArg } from "./fakes.ts";

const ctx = { db: {} as never };

describe("faq", () => {
	it("replies with the entry for the subcommand", async () => {
		const [name, entry] = Object.entries(FAQ_ENTRIES)[0] as [
			string,
			(typeof FAQ_ENTRIES)[string],
		];
		const interaction = fakeInteraction({ subcommand: name });
		await faq(asCommand(interaction), ctx);

		const payload = firstArg<{
			embeds: { title: string; description: string }[];
		}>(interaction.reply);
		expect(payload.embeds[0]?.title).toBe(entry.title);
		expect(payload.embeds[0]?.description).toBe(entry.description);
	});

	it("answers unknown sections privately", async () => {
		const interaction = fakeInteraction({ subcommand: "nope" });
		await faq(asCommand(interaction), ctx);

		const payload = firstArg<{ flags: number }>(interaction.reply);
		expect(payload.flags).toBe(MessageFlags.Ephemeral);
	});

	it("registers a subcommand for every entry", () => {
		expect(FAQ_COMMAND.options?.map((option) => option.name)).toEqual(
			Object.keys(FAQ_ENTRIES),
		);
		expect(COMMANDS).toContain(FAQ_COMMAND);
	});
});
