/**
 * The Worker entry point: verifies that requests come from Discord and routes
 * interactions to command handlers.
 *
 * https://discord.com/developers/docs/interactions/receiving-and-responding
 */
import {
  ApplicationCommandType,
  InteractionResponseType,
  InteractionType,
  type APIChatInputApplicationCommandInteraction,
  type APIInteraction,
} from "discord-api-types/v10";
import { verifyKey } from "discord-interactions";
import { AutoRouter, type IRequest } from "itty-router";

import {
  FAQ_COMMAND,
  RUSNI_PYZDA_COMMAND,
  SLAP_COMMAND,
  SUM20_COMMAND,
  SUM_COMMAND,
} from "./commands.ts";
import {
  JsonResponse,
  ephemeralError,
  type CommandHandler,
} from "./discord.ts";
import type { Env } from "./env.ts";
import { faq } from "./handlers/faq.ts";
import { rusniPyzda } from "./handlers/rusni_pyzda.ts";
import { slap } from "./handlers/slap.ts";
import { sum } from "./handlers/sum.ts";
import { sum20 } from "./handlers/sum20.ts";

const HANDLERS: Record<string, CommandHandler> = {
  [FAQ_COMMAND.name]: faq,
  [SLAP_COMMAND.name]: slap,
  [SUM_COMMAND.name]: sum,
  [SUM20_COMMAND.name]: sum20,
  [RUSNI_PYZDA_COMMAND.name]: rusniPyzda,
};

type VerifiedRequest =
  | { isValid: true; interaction: APIInteraction }
  | { isValid: false; interaction?: undefined };

export async function verifyDiscordRequest(
  request: Request,
  env: Env,
): Promise<VerifiedRequest> {
  const signature = request.headers.get("x-signature-ed25519");
  const timestamp = request.headers.get("x-signature-timestamp");
  const body = await request.text();
  const isValid =
    signature !== null &&
    timestamp !== null &&
    (await verifyKey(body, signature, timestamp, env.DISCORD_PUBLIC_KEY));
  if (!isValid) {
    return { isValid: false };
  }
  return { isValid: true, interaction: JSON.parse(body) as APIInteraction };
}

const router = AutoRouter<IRequest, [Env, ExecutionContext]>();

/** A hello page to check that the worker is deployed. */
router.get(
  "/",
  (_request, env) => new Response(`👋 ${env.DISCORD_APPLICATION_ID}`),
);

/** Discord sends every interaction here, see the Interactions Endpoint URL. */
router.post("/", async (request, env, ctx) => {
  const verified = await verifyDiscordRequest(request, env);
  if (!verified.isValid) {
    return new Response("Bad request signature.", { status: 401 });
  }
  const { interaction } = verified;

  if (interaction.type === InteractionType.Ping) {
    return new JsonResponse({ type: InteractionResponseType.Pong });
  }

  if (
    interaction.type === InteractionType.ApplicationCommand &&
    interaction.data.type === ApplicationCommandType.ChatInput
  ) {
    const handler = HANDLERS[interaction.data.name];
    if (!handler) {
      return new JsonResponse({ error: "Unknown command" }, { status: 400 });
    }
    try {
      return new JsonResponse(
        await handler(
          interaction as APIChatInputApplicationCommandInteraction,
          env,
          ctx,
        ),
      );
    } catch (error) {
      console.error(error);
      return new JsonResponse(ephemeralError("Помилка", String(error)));
    }
  }

  return new JsonResponse(
    { error: "Unknown interaction type" },
    { status: 400 },
  );
});

router.all("*", () => new Response("Not Found.", { status: 404 }));

export default {
  fetch: (request, env, ctx) => router.fetch(request, env, ctx),
} satisfies ExportedHandler<Env>;
