import { InteractionResponseType } from "discord-api-types/v10";
import { beforeAll, describe, expect, it } from "vitest";

import { Color } from "../src/discord.ts";
import { RUSSIAN_WARSHIP_API } from "../src/handlers/rusni_pyzda.ts";
import { dispatch } from "./harness.ts";
import { chatInputInteraction, createSigner, type Signer } from "./helpers.ts";

const today = () => new Date().toISOString().slice(0, 10);

let signer: Signer;

beforeAll(async () => {
  signer = await createSigner();
});

async function lookup(response: Response) {
  const outcome = await dispatch(
    signer,
    chatInputInteraction("rusni_pyzda"),
    (request) => {
      expect(request.url).toBe(`${RUSSIAN_WARSHIP_API}/statistics/latest`);
      return response;
    },
  );
  expect(outcome.body).toEqual({
    type: InteractionResponseType.DeferredChannelMessageWithSource,
  });
  return outcome.edited?.embeds?.[0];
}

describe("/rusni_pyzda", () => {
  it("lists every stat with its daily increase", async () => {
    const embed = await lookup(
      Response.json({
        message: "The data were fetched successfully.",
        data: {
          date: today(),
          day: 1653,
          resource: "https://www.facebook.com/GeneralStaff.ua",
          stats: { personnel_units: 1000000, tanks: 11000 },
          increase: { personnel_units: 1200, tanks: 5 },
        },
      }),
    );

    expect(embed?.title).toBe("Втрати ворога");
    expect(embed?.url).toBe("https://www.facebook.com/GeneralStaff.ua");
    expect(embed?.fields).toEqual([
      { name: "personnel_units", value: "1000000 (+1200)", inline: true },
      { name: "tanks", value: "11000 (+5)", inline: true },
    ]);
    expect(embed?.footer?.text).toBe(`Станом на ${today()}, 1653й день війни`);
    expect(embed?.thumbnail?.url).toContain(
      "Emblem_of_the_Ukrainian_Armed_Forces",
    );
  });

  it("shows the API error message", async () => {
    const embed = await lookup(
      Response.json(
        {
          message: "Statistics for this date are not found.",
          errors: { date: ["not found"] },
        },
        { status: 404 },
      ),
    );

    expect(embed?.title).toBe("Втрати ворога: помилка");
    expect(embed?.description).toBe("Statistics for this date are not found.");
    expect(embed?.color).toBe(Color.red);
  });

  it("reports upstream failures in the edited response", async () => {
    const outcome = await dispatch(
      signer,
      chatInputInteraction("rusni_pyzda"),
      () => {
        throw new Error("connection refused");
      },
    );

    const embed = outcome.edited?.embeds?.[0];
    expect(embed?.title).toBe("Помилка");
    // Internal detail stays in the logs, not in a public channel.
    expect(embed?.description).toBe("Спробуйте ще раз пізніше.");
  });
});
