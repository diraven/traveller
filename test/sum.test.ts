import { beforeAll, describe, expect, it } from "vitest";

import { SUM_URL } from "../src/handlers/sum.ts";
import { failing, runDeferred, type Upstream } from "./deferred.ts";
import {
  chatInputInteraction,
  createSigner,
  stringOption,
  type Signer,
} from "./helpers.ts";

const WORD = "слово";
const LOOKUP_URL = `${SUM_URL}?swrd=${encodeURIComponent(WORD)}`;

function article(body: string, volume: string): string {
  return `<div itemtype="http://schema.org/ScholarlyArticle">
    <div itemprop="articleBody">${body}</div>
    <p class="tom">${volume}</p>
  </div>`;
}

function site(html: string) {
  return (request: Request) => {
    expect(request.url).toBe(LOOKUP_URL);
    return new Response(`<html><body>${html}</body></html>`);
  };
}

let signer: Signer;

beforeAll(async () => {
  signer = await createSigner();
});

const lookup = (upstream: Upstream) =>
  runDeferred(
    signer,
    chatInputInteraction("sum", [stringOption("word", WORD)]),
    upstream,
  );

describe("/sum", () => {
  it("shows the first article with its volume", async () => {
    const edited = await lookup(
      site(
        article(
          "<b>СЛО́ВО</b>, а, <i>с.</i> 1. Мовна одиниця",
          "Том 9, стор. 367",
        ),
      ),
    );

    const embed = edited.embeds?.[0];
    expect(embed?.author).toEqual({ name: "sum.in.ua", url: LOOKUP_URL });
    expect(embed?.description).toBe("СЛО́ВО, а, с. 1. Мовна одиниця");
    expect(embed?.footer?.text).toBe("Том 9, стор. 367");
  });

  it("links to the site when there are several meanings", async () => {
    const edited = await lookup(
      site(article("перше", "Том 1") + article("друге", "Том 2")),
    );

    const embed = edited.embeds?.[0];
    expect(embed?.description).toBe(
      `перше\n\nСлово має [більше одного значення](${LOOKUP_URL}).`,
    );
    expect(embed?.footer?.text).toBe("Том 1");
  });

  it("reports missing words", async () => {
    const edited = await lookup(site("<p>Нічого</p>"));

    expect(edited.embeds?.[0]?.description).toBe(
      `Слово не знайдено. Що в біса таке '${WORD}'?`,
    );
  });

  it("truncates long articles", async () => {
    const edited = await lookup(site(article("x".repeat(5000), "Том")));

    expect(edited.embeds?.[0]?.description).toBe(`${"x".repeat(2000)}...`);
  });

  it("reports upstream failures in the edited response", async () => {
    const edited = await lookup(failing("connection refused"));

    const embed = edited.embeds?.[0];
    expect(embed?.title).toBe("Помилка");
    expect(embed?.description).toContain("connection refused");
  });
});
