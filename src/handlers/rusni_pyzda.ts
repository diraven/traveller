import type { APIEmbed } from "discord-api-types/v10";

import { Color, deferred, type CommandHandler } from "../discord.ts";

export const RUSSIAN_WARSHIP_API = "https://russianwarship.rip/api/v2";

const THUMBNAIL_URL =
  "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_the_Ukrainian_Armed_Forces.svg/1024px-Emblem_of_the_Ukrainian_Armed_Forces.svg.png";

interface StatisticsResponse {
  message?: string;
  errors?: unknown;
  data?: {
    date: string;
    day: number;
    resource: string;
    stats: Record<string, number>;
    increase: Record<string, number>;
  };
}

export async function fetchLosses(): Promise<APIEmbed> {
  const response = await fetch(`${RUSSIAN_WARSHIP_API}/statistics/latest`);
  const payload = (await response.json()) as StatisticsResponse;

  if (payload.errors || !payload.data) {
    return {
      title: "Втрати ворога: помилка",
      description: payload.message ?? "Невідома помилка.",
      color: Color.red,
    };
  }

  const { data } = payload;
  return {
    title: "Втрати ворога",
    url: data.resource,
    fields: Object.entries(data.stats).map(([name, value]) => ({
      name,
      value: `${value} (+${data.increase[name] ?? 0})`,
      inline: true,
    })),
    footer: { text: `Станом на ${data.date}, ${data.day}й день війни` },
    thumbnail: { url: THUMBNAIL_URL },
  };
}

export const rusniPyzda: CommandHandler = (interaction, env, ctx) =>
  deferred(interaction, env, ctx, async () => ({
    embeds: [await fetchLosses()],
  }));
