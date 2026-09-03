/**
 * Text extraction from HTML using the Workers-native streaming HTMLRewriter,
 * replacing BeautifulSoup from the Python version.
 */

const NAMED_ENTITIES: Record<string, string> = {
  amp: "&",
  lt: "<",
  gt: ">",
  quot: '"',
  apos: "'",
  nbsp: "\u00a0",
};

export function decodeEntities(text: string): string {
  return text.replace(
    /&(#x[0-9a-f]+|#\d+|[a-z]+);/gi,
    (match: string, entity: string) => {
      if (entity.startsWith("#x") || entity.startsWith("#X")) {
        return String.fromCodePoint(parseInt(entity.slice(2), 16));
      }
      if (entity.startsWith("#")) {
        return String.fromCodePoint(parseInt(entity.slice(1), 10));
      }
      return NAMED_ENTITIES[entity.toLowerCase()] ?? match;
    },
  );
}

/**
 * Collects the text content of every element matching each selector, in
 * document order, in a single pass over the document.
 */
export async function selectTexts<Selectors extends Record<string, string>>(
  html: string,
  selectors: Selectors,
): Promise<Record<keyof Selectors, string[]>> {
  const results = {} as Record<keyof Selectors, string[]>;
  const rewriter = new HTMLRewriter();

  for (const [key, selector] of Object.entries(selectors) as [
    keyof Selectors,
    string,
  ][]) {
    const texts: string[] = [];
    results[key] = texts;
    rewriter.on(selector, {
      element() {
        texts.push("");
      },
      text(chunk) {
        const index = texts.length - 1;
        texts[index] = (texts[index] ?? "") + chunk.text;
      },
    });
  }

  // The transformation is streaming and lazy, so the body has to be consumed.
  await rewriter.transform(new Response(html)).text();

  for (const key of Object.keys(results) as (keyof Selectors)[]) {
    results[key] = results[key].map(decodeEntities);
  }
  return results;
}

/** Strips all tags from an HTML fragment, like BeautifulSoup's `.text`. */
export async function htmlToText(html: string): Promise<string> {
  const { root } = await selectTexts(`<div id="root">${html}</div>`, {
    root: "#root",
  });
  return root[0] ?? "";
}
