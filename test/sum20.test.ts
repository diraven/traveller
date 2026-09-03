import { beforeAll, describe, expect, it } from "vitest";

import { SUM20_URL } from "../src/handlers/sum20.ts";
import { runDeferred } from "./deferred.ts";
import {
  chatInputInteraction,
  createSigner,
  stringOption,
  type Signer,
} from "./helpers.ts";

const WORD = "слово";
const URL = `${SUM20_URL}/api/DictEntry/searchEntry/${encodeURIComponent(WORD)}`;

let signer: Signer;

beforeAll(async () => {
  signer = await createSigner();
});

const lookup = (response: Response) =>
  runDeferred(
    signer,
    chatInputInteraction("sum20", [stringOption("word", WORD)]),
    (request) => {
      expect(request.url).toBe(URL);
      return response;
    },
  );

describe("/sum20", () => {
  it("renders the entry as plain text", async () => {
    const edited = await lookup(
      Response.json({
        entry: "<p><b>СЛО́ВО</b>, а, <i>с.</i></p><p>1. Мовна одиниця.</p>",
      }),
    );

    const embed = edited.embeds?.[0];
    expect(embed?.author).toEqual({ name: "sum20ua.com", url: SUM20_URL });
    expect(embed?.description).toBe("СЛО́ВО, а, с.1. Мовна одиниця.");
  });

  it("reports missing words on a non-2xx answer", async () => {
    const edited = await lookup(Response.json({}, { status: 404 }));

    expect(edited.embeds?.[0]?.description).toBe(
      `Слово не знайдено. Що в біса таке '${WORD}'?`,
    );
  });
});
