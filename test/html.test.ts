import { describe, expect, it } from "vitest";

import { decodeEntities, htmlToText, selectTexts } from "../src/html.ts";

describe("decodeEntities", () => {
  it("decodes named, decimal and hex entities", () => {
    expect(
      decodeEntities("a &amp; b &lt;c&gt; &quot;d&quot; &#39;e&#39;"),
    ).toBe("a & b <c> \"d\" 'e'");
    expect(decodeEntities("&#1057;&#x43B;&nbsp;x")).toBe("Сл\u00a0x");
  });

  it("leaves unknown entities alone", () => {
    expect(decodeEntities("&bogus; &")).toBe("&bogus; &");
  });
});

describe("selectTexts", () => {
  const html = `
    <html><body>
      <div class="a"><p>one &amp; <b>two</b></p></div>
      <div class="a">three</div>
      <div class="b" data-x="y">four</div>
    </body></html>`;

  it("collects text per matching element in document order", async () => {
    const result = await selectTexts(html, {
      a: "div.a",
      b: 'div[data-x="y"]',
      nested: "div.a b",
      missing: "span",
    });
    expect(result.a).toEqual(["one & two", "three"]);
    expect(result.b).toEqual(["four"]);
    expect(result.nested).toEqual(["two"]);
    expect(result.missing).toEqual([]);
  });
});

describe("htmlToText", () => {
  it("strips tags from a fragment", async () => {
    expect(await htmlToText("<p><b>Сло&#769;во</b>, -а, <i>с.</i></p>")).toBe(
      "Сло́во, -а, с.",
    );
  });

  it("handles empty input", async () => {
    expect(await htmlToText("")).toBe("");
  });
});
