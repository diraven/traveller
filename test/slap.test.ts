import { userMention } from "discord.js";
import { describe, expect, it } from "vitest";

import { renderSlap, SLAP_TEMPLATES, slap } from "../src/handlers/slap.ts";
import { asCommand, fakeInteraction, fakeUser, firstArg } from "./fakes.ts";

describe("renderSlap", () => {
	it("substitutes both mentions", () => {
		expect(renderSlap("{actor} hits {target}.", "1", "2")).toBe(
			`${userMention("1")} hits ${userMention("2")}.`,
		);
	});

	it("leaves every template with no placeholders behind", () => {
		for (const template of SLAP_TEMPLATES) {
			const rendered = renderSlap(template, "1", "2");
			expect(rendered).not.toContain("{actor}");
			expect(rendered).not.toContain("{target}");
		}
	});
});

describe("slap", () => {
	it("replies with a rendered template", async () => {
		const interaction = fakeInteraction({
			user: fakeUser({ id: "1" }),
			users: { member: fakeUser({ id: "2" }) },
		});
		await slap(asCommand(interaction), { db: {} as never });

		const payload = firstArg<{
			embeds: { title: string; description: string }[];
		}>(interaction.reply);
		const embed = payload.embeds[0];
		expect(embed?.title).toBe("Йой!");
		expect(embed?.description).toContain(userMention("1"));
		expect(embed?.description).toContain(userMention("2"));
	});
});
