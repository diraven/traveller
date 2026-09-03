/**
 * Shared harness for commands that defer and then edit the original response
 * through the interaction webhook. Outbound `fetch` is stubbed, as the
 * Cloudflare Vitest integration recommends.
 */
import {
  createExecutionContext,
  waitOnExecutionContext,
} from "cloudflare:test";
import {
  InteractionResponseType,
  type APIInteraction,
  type RESTPatchAPIInteractionOriginalResponseJSONBody,
} from "discord-api-types/v10";
import { expect, vi } from "vitest";

import { API_BASE } from "../src/discord.ts";
import worker from "../src/server.ts";
import {
  APPLICATION_ID,
  INTERACTION_TOKEN,
  serialize,
  type Signer,
} from "./helpers.ts";

export type Upstream = (request: Request) => Response | Promise<Response>;

const EDIT_ORIGINAL_URL = `${API_BASE}/webhooks/${APPLICATION_ID}/${INTERACTION_TOKEN}/messages/@original`;

/**
 * Sends the interaction, asserts it was deferred, routes every other outbound
 * request to `upstream`, and returns the body Discord was asked to show.
 */
export async function runDeferred(
  signer: Signer,
  interaction: APIInteraction,
  upstream: Upstream,
): Promise<RESTPatchAPIInteractionOriginalResponseJSONBody> {
  let edited: RESTPatchAPIInteractionOriginalResponseJSONBody | undefined;

  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const request = new Request(input, init);
      if (request.method === "PATCH" && request.url === EDIT_ORIGINAL_URL) {
        expect(edited, "original response edited twice").toBeUndefined();
        edited =
          (await request.json()) as RESTPatchAPIInteractionOriginalResponseJSONBody;
        return Response.json({});
      }
      return upstream(request);
    }),
  );

  try {
    const ctx = createExecutionContext();
    const response = await worker.fetch(
      await signer.sign(serialize(interaction)),
      signer.env,
      ctx,
    );
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({
      type: InteractionResponseType.DeferredChannelMessageWithSource,
    });
    await waitOnExecutionContext(ctx);
  } finally {
    vi.unstubAllGlobals();
  }

  if (!edited) {
    throw new Error("The original response was never edited.");
  }
  return edited;
}

/** An upstream that fails every request, standing in for network errors. */
export function failing(message: string): Upstream {
  return () => {
    throw new Error(message);
  };
}
