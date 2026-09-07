import {
	createExecutionContext,
	waitOnExecutionContext,
} from "cloudflare:test";
import {
	type APIInteractionResponseChannelMessageWithSource,
	InteractionResponseType,
} from "discord-api-types/v10";
import { beforeAll, describe, expect, it } from "vitest";

import { Color } from "../src/discord.ts";
import { renderSlap, SLAP_TEMPLATES } from "../src/handlers/slap.ts";
import worker from "../src/server.ts";
import {
	chatInputInteraction,
	createSigner,
	INVOKER_ID,
	type Signer,
	serialize,
	TARGET_ID,
	userOption,
} from "./helpers.ts";

let signer: Signer;

beforeAll(async () => {
	signer = await createSigner();
});

describe("/slap", () => {
	it("mentions both the invoker and the target", async () => {
		const ctx = createExecutionContext();
		const response = await worker.fetch(
			await signer.sign(
				serialize(
					chatInputInteraction("slap", [userOption("member", TARGET_ID)]),
				),
			),
			signer.env,
			ctx,
		);
		await waitOnExecutionContext(ctx);

		expect(response.status).toBe(200);
		const body =
			(await response.json()) as APIInteractionResponseChannelMessageWithSource;
		expect(body.type).toBe(InteractionResponseType.ChannelMessageWithSource);
		const embed = body.data.embeds?.[0];
		expect(embed?.title).toBe("Йой!");
		expect(embed?.color).toBe(Color.blue);

		const expected = SLAP_TEMPLATES.map((template) =>
			renderSlap(template, INVOKER_ID, TARGET_ID),
		);
		expect(expected).toContain(embed?.description);
		expect(embed?.description).toContain(`<@${INVOKER_ID}>`);
		expect(embed?.description).toContain(`<@${TARGET_ID}>`);
	});

	it("has an actor and a target in every template", () => {
		for (const template of SLAP_TEMPLATES) {
			expect(template).toContain("{actor}");
			expect(template).toContain("{target}");
		}
	});
});
