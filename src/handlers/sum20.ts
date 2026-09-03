import type { APIEmbed } from "discord-api-types/v10";

import {
  deferred,
  getStringOption,
  truncate,
  type CommandHandler,
} from "../discord.ts";
import { htmlToText } from "../html.ts";

export const SUM20_URL = "https://sum20ua.com";

interface Sum20Entry {
  entry?: string;
}

export async function lookupSum20(word: string): Promise<APIEmbed> {
  const response = await fetch(
    `${SUM20_URL}/api/DictEntry/searchEntry/${encodeURIComponent(word)}`,
  );
  const embed: APIEmbed = { author: { name: "sum20ua.com", url: SUM20_URL } };
  if (!response.ok) {
    embed.description = `Слово не знайдено. Що в біса таке '${word}'?`;
    return embed;
  }
  const data = (await response.json()) as Sum20Entry;
  embed.description = truncate(await htmlToText(data.entry ?? ""), 2000);
  return embed;
}

export const sum20: CommandHandler = (interaction, env, ctx) =>
  deferred(interaction, env, ctx, async () => ({
    embeds: [await lookupSum20(getStringOption(interaction, "word"))],
  }));
