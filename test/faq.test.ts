import {
  createExecutionContext,
  waitOnExecutionContext,
} from "cloudflare:test";
import {
  InteractionResponseType,
  MessageFlags,
  type APIInteractionResponseChannelMessageWithSource,
} from "discord-api-types/v10";
import { beforeAll, describe, expect, it } from "vitest";

import { FAQ_COMMAND } from "../src/commands.ts";
import { FAQ_ENTRIES } from "../src/faq_entries.ts";
import worker from "../src/server.ts";
import {
  chatInputInteraction,
  createSigner,
  serialize,
  subcommand,
  type Signer,
} from "./helpers.ts";

let signer: Signer;

beforeAll(async () => {
  signer = await createSigner();
});

async function faq(name: string) {
  const ctx = createExecutionContext();
  const response = await worker.fetch(
    await signer.sign(
      serialize(chatInputInteraction("faq", [subcommand(name)])),
    ),
    signer.env,
    ctx,
  );
  await waitOnExecutionContext(ctx);
  expect(response.status).toBe(200);
  return (await response.json()) as APIInteractionResponseChannelMessageWithSource;
}

describe("/faq", () => {
  it("registers one subcommand per entry", () => {
    expect(FAQ_COMMAND.options?.map((option) => option.name)).toEqual(
      Object.keys(FAQ_ENTRIES),
    );
    for (const option of FAQ_COMMAND.options ?? []) {
      expect(option.description.length).toBeLessThanOrEqual(100);
    }
  });

  it.each(Object.keys(FAQ_ENTRIES))("answers %s", async (name) => {
    const entry = FAQ_ENTRIES[name];
    const body = await faq(name);
    expect(body.type).toBe(InteractionResponseType.ChannelMessageWithSource);
    const embed = body.data.embeds?.[0];
    expect(embed?.title).toBe(entry?.title);
    expect(embed?.description).toBe(entry?.description);
    expect(embed?.image?.url).toBe(entry?.image);
  });

  it("rejects unknown entries with an ephemeral error", async () => {
    const body = await faq("nope");
    expect(body.data.flags).toBe(MessageFlags.Ephemeral);
    expect(body.data.embeds?.[0]?.title).toBe("Помилка");
  });
});
