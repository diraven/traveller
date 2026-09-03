/**
 * Small helpers around the Discord interactions API. Anything that touches
 * the Discord REST API lives here so handlers stay declarative.
 */
import {
  ApplicationCommandOptionType,
  InteractionResponseType,
  MessageFlags,
  type APIApplicationCommandInteractionDataOption,
  type APIChatInputApplicationCommandInteraction,
  type APIEmbed,
  type APIInteractionResponse,
  type APIInteractionResponseCallbackData,
  type RESTPatchAPIInteractionOriginalResponseJSONBody,
} from "discord-api-types/v10";

import type { Env } from "./env.ts";

export const API_BASE = "https://discord.com/api/v10";

/** Embed colors matching discord.py's `discord.Color` presets. */
export const Color = {
  red: 0xe74c3c,
  green: 0x2ecc71,
  blue: 0x3498db,
} as const;

export type CommandHandler = (
  interaction: APIChatInputApplicationCommandInteraction,
  env: Env,
  ctx: ExecutionContext,
) => Promise<APIInteractionResponse> | APIInteractionResponse;

export class JsonResponse extends Response {
  constructor(body: unknown, init?: ResponseInit) {
    super(JSON.stringify(body), {
      ...init,
      headers: {
        "content-type": "application/json;charset=UTF-8",
        ...init?.headers,
      },
    });
  }
}

export function message(
  data: APIInteractionResponseCallbackData,
): APIInteractionResponse {
  return { type: InteractionResponseType.ChannelMessageWithSource, data };
}

export function embedMessage(embed: APIEmbed): APIInteractionResponse {
  return message({ embeds: [embed] });
}

export function errorEmbed(title: string, description: string): APIEmbed {
  return { title, description, color: Color.red };
}

export function ephemeralError(
  title: string,
  description: string,
): APIInteractionResponse {
  return message({
    embeds: [errorEmbed(title, description)],
    flags: MessageFlags.Ephemeral,
  });
}

/**
 * Discord requires an answer within 3 seconds. Handlers that call external
 * services acknowledge immediately and finish the work in the background,
 * then edit the original response.
 */
export function deferred(
  interaction: APIChatInputApplicationCommandInteraction,
  env: Env,
  ctx: ExecutionContext,
  work: () => Promise<APIInteractionResponseCallbackData>,
): APIInteractionResponse {
  ctx.waitUntil(
    work()
      .catch((error: unknown) => {
        console.error(error);
        return { embeds: [errorEmbed("Помилка", String(error))] };
      })
      .then((data) => editOriginalResponse(env, interaction.token, data)),
  );
  return { type: InteractionResponseType.DeferredChannelMessageWithSource };
}

export async function editOriginalResponse(
  env: Env,
  interactionToken: string,
  data: RESTPatchAPIInteractionOriginalResponseJSONBody,
): Promise<void> {
  const url = `${API_BASE}/webhooks/${env.DISCORD_APPLICATION_ID}/${interactionToken}/messages/@original`;
  const response = await fetch(url, {
    method: "PATCH",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(
      `Failed to edit original response: ${response.status} ${await response.text()}`,
    );
  }
}

export function getOptions(
  interaction: APIChatInputApplicationCommandInteraction,
): APIApplicationCommandInteractionDataOption[] {
  return interaction.data.options ?? [];
}

export function getSubcommandName(
  interaction: APIChatInputApplicationCommandInteraction,
): string | undefined {
  const option = getOptions(interaction)[0];
  return option?.type === ApplicationCommandOptionType.Subcommand
    ? option.name
    : undefined;
}

export function getStringOption(
  interaction: APIChatInputApplicationCommandInteraction,
  name: string,
): string {
  const option = getOptions(interaction).find(
    (candidate) => candidate.name === name,
  );
  if (option?.type !== ApplicationCommandOptionType.String) {
    throw new Error(`Missing string option "${name}".`);
  }
  return option.value;
}

/** Returns the user id (snowflake) chosen in a user option. */
export function getUserOption(
  interaction: APIChatInputApplicationCommandInteraction,
  name: string,
): string {
  const option = getOptions(interaction).find(
    (candidate) => candidate.name === name,
  );
  if (option?.type !== ApplicationCommandOptionType.User) {
    throw new Error(`Missing user option "${name}".`);
  }
  return option.value;
}

export function getInvokerId(
  interaction: APIChatInputApplicationCommandInteraction,
): string {
  const user = interaction.member?.user ?? interaction.user;
  if (!user) {
    throw new Error("Interaction has no user.");
  }
  return user.id;
}

export function userMention(userId: string): string {
  return `<@${userId}>`;
}

export function truncate(text: string, maxLength: number): string {
  return text.length < maxLength ? text : `${text.slice(0, maxLength)}...`;
}
