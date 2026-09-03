import { beforeAll, describe, expect, it } from "vitest";

import { Color } from "../src/discord.ts";
import { RUSSIAN_WARSHIP_API } from "../src/handlers/rusni_pyzda.ts";
import { runDeferred } from "./deferred.ts";
import { chatInputInteraction, createSigner, type Signer } from "./helpers.ts";

const today = () => new Date().toISOString().slice(0, 10);

let signer: Signer;

beforeAll(async () => {
  signer = await createSigner();
});

const lookup = (response: Response) =>
  runDeferred(signer, chatInputInteraction("rusni_pyzda"), (request) => {
    expect(request.url).toBe(`${RUSSIAN_WARSHIP_API}/statistics/latest`);
    return response;
  });

describe("/rusni_pyzda", () => {
  it("lists every stat with its daily increase", async () => {
    const edited = await lookup(
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

    const embed = edited.embeds?.[0];
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
    const edited = await lookup(
      Response.json(
        {
          message: "Statistics for this date are not found.",
          errors: { date: ["not found"] },
        },
        { status: 404 },
      ),
    );

    const embed = edited.embeds?.[0];
    expect(embed?.title).toBe("Втрати ворога: помилка");
    expect(embed?.description).toBe("Statistics for this date are not found.");
    expect(embed?.color).toBe(Color.red);
  });
});
