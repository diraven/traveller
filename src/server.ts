/**
 * The Worker entry point: verifies that requests come from Discord and routes
 * interactions to command and component handlers.
 *
 * https://discord.com/developers/docs/interactions/receiving-and-responding
 */
import {
  ApplicationCommandType,
  InteractionResponseType,
  InteractionType,
  type APIChatInputApplicationCommandInteraction,
  type APIInteraction,
  type APIInteractionResponse,
  type APIUserApplicationCommandInteraction,
} from "discord-api-types/v10";
import { verifyKey } from "discord-interactions";
import { AutoRouter, type IRequest } from "itty-router";

import {
  BANS_SHARING_COMMAND,
  FAQ_COMMAND,
  RUSNI_PYZDA_COMMAND,
  SHARE_BAN_USER_COMMAND,
  SLAP_COMMAND,
  VERIFICATION_COMMAND,
  VERIFY_COMMAND,
} from "./commands.ts";
import {
  JsonResponse,
  ephemeralError,
  userFacingMessage,
  type CommandHandler,
  type ComponentHandler,
  type UserCommandHandler,
} from "./discord.ts";
import type { Env } from "./env.ts";
import {
  BAN_BUTTON_ID,
  SKIP_BUTTON_ID,
  banButton,
  bansSharing,
  shareBanUserCommand,
  skipButton,
} from "./handlers/bans_sharing.ts";
import { faq } from "./handlers/faq.ts";
import { rusniPyzda } from "./handlers/rusni_pyzda.ts";
import { slap } from "./handlers/slap.ts";
import { verification, verify } from "./handlers/verification.ts";

const CHAT_INPUT_HANDLERS: Record<string, CommandHandler> = {
  [FAQ_COMMAND.name]: faq,
  [SLAP_COMMAND.name]: slap,
  [RUSNI_PYZDA_COMMAND.name]: rusniPyzda,
  [VERIFICATION_COMMAND.name]: verification,
  [VERIFY_COMMAND.name]: verify,
  [BANS_SHARING_COMMAND.name]: bansSharing,
};

const USER_COMMAND_HANDLERS: Record<string, UserCommandHandler> = {
  [SHARE_BAN_USER_COMMAND.name]: shareBanUserCommand,
};

const COMPONENT_HANDLERS: Record<string, ComponentHandler> = {
  [BAN_BUTTON_ID]: banButton,
  [SKIP_BUTTON_ID]: skipButton,
};

type VerifiedRequest =
  | { isValid: true; interaction: APIInteraction }
  | { isValid: false; interaction?: undefined };

/** How far a request's signed timestamp may be from now, in seconds. */
const MAX_TIMESTAMP_SKEW = 300;

export async function verifyDiscordRequest(
  request: Request,
  env: Env,
): Promise<VerifiedRequest> {
  const signature = request.headers.get("x-signature-ed25519");
  const timestamp = request.headers.get("x-signature-timestamp");
  if (signature === null || timestamp === null) {
    return { isValid: false };
  }

  // The signature covers the timestamp, so checking its age stops a captured
  // request being replayed later in the interaction token's lifetime.
  const age = Math.abs(Date.now() / 1000 - Number(timestamp));
  if (!Number.isFinite(age) || age > MAX_TIMESTAMP_SKEW) {
    return { isValid: false };
  }

  const body = await request.text();
  if (!(await verifyKey(body, signature, timestamp, env.DISCORD_PUBLIC_KEY))) {
    return { isValid: false };
  }
  return { isValid: true, interaction: JSON.parse(body) as APIInteraction };
}

/** Picks the handler for an interaction, or undefined when there is none. */
function route(
  interaction: APIInteraction,
  env: Env,
  ctx: ExecutionContext,
): Promise<APIInteractionResponse> | APIInteractionResponse | undefined {
  if (interaction.type === InteractionType.ApplicationCommand) {
    if (interaction.data.type === ApplicationCommandType.ChatInput) {
      return CHAT_INPUT_HANDLERS[interaction.data.name]?.(
        interaction as APIChatInputApplicationCommandInteraction,
        env,
        ctx,
      );
    }
    if (interaction.data.type === ApplicationCommandType.User) {
      return USER_COMMAND_HANDLERS[interaction.data.name]?.(
        interaction as APIUserApplicationCommandInteraction,
        env,
        ctx,
      );
    }
  }
  if (interaction.type === InteractionType.MessageComponent) {
    return COMPONENT_HANDLERS[interaction.data.custom_id]?.(
      interaction,
      env,
      ctx,
    );
  }
  return undefined;
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

  try {
    const response = await route(interaction, env, ctx);
    if (!response) {
      return new JsonResponse(
        { error: "Unknown interaction" },
        { status: 400 },
      );
    }
    return new JsonResponse(response);
  } catch (error) {
    console.error(error);
    return new JsonResponse(
      ephemeralError("Помилка", userFacingMessage(error)),
    );
  }
});

router.all("*", () => new Response("Not Found.", { status: 404 }));

export default {
  fetch: (request, env, ctx) => router.fetch(request, env, ctx),
} satisfies ExportedHandler<Env>;
