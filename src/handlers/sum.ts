import type { APIEmbed } from "discord-api-types/v10";

import {
  deferred,
  getStringOption,
  truncate,
  type CommandHandler,
} from "../discord.ts";
import { selectTexts } from "../html.ts";

// The site is served over plain HTTP, same as the Python version used.
export const SUM_URL = "http://sum.in.ua/";

const ARTICLE = 'div[itemtype="http://schema.org/ScholarlyArticle"]';

export async function lookupSum(word: string): Promise<APIEmbed> {
  const url = `${SUM_URL}?swrd=${encodeURIComponent(word)}`;
  const embed: APIEmbed = { author: { name: "sum.in.ua", url } };

  const response = await fetch(url);
  const { articles, bodies, volumes } = await selectTexts(
    await response.text(),
    {
      articles: ARTICLE,
      bodies: `${ARTICLE} div[itemprop="articleBody"]`,
      volumes: `${ARTICLE} p.tom`,
    },
  );

  if (articles.length === 0) {
    embed.description = `Слово не знайдено. Що в біса таке '${word}'?`;
    return embed;
  }

  embed.description = truncate(bodies[0] ?? "Текст не знайдено", 2000);
  embed.footer = { text: truncate(volumes[0] ?? "Том не знайдено", 1000) };
  if (articles.length > 1) {
    embed.description += `\n\nСлово має [більше одного значення](${url}).`;
  }
  return embed;
}

export const sum: CommandHandler = (interaction, env, ctx) =>
  deferred(interaction, env, ctx, async () => ({
    embeds: [await lookupSum(getStringOption(interaction, "word"))],
  }));
