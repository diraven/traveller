/**
 * Sends a signed interaction through the worker with outbound `fetch`
 * stubbed, as the Cloudflare Vitest integration recommends. Records every
 * Discord API call the handler makes and captures the deferred edit of the
 * original response.
 */
import {
	createExecutionContext,
	waitOnExecutionContext,
} from "cloudflare:test";
import type {
	APIEmbed,
	APIInteraction,
	APIInteractionResponse,
} from "discord-api-types/v10";
import { expect, vi } from "vitest";

import { API_BASE } from "../src/discord.ts";
import worker from "../src/server.ts";
import {
	APPLICATION_ID,
	INTERACTION_TOKEN,
	type Signer,
	serialize,
} from "./helpers.ts";

export interface RecordedRequest {
	method: string;
	url: string;
	/** Path relative to the Discord API base, when the request targets it. */
	path: string;
	headers: Headers;
	body: unknown;
}

export type Upstream = (
	request: Request,
	recorded: RecordedRequest,
) => Response | Promise<Response>;

/** What a handler sends, either immediately or in a deferred edit. */
export interface ResponseData {
	content?: string | undefined;
	embeds?: APIEmbed[] | undefined;
	flags?: number | undefined;
	components?: unknown[] | undefined;
}

export interface Outcome {
	status: number;
	body: APIInteractionResponse;
	/** Body of the deferred edit of the original response, if one happened. */
	edited?: ResponseData | undefined;
	requests: RecordedRequest[];
}

const EDIT_ORIGINAL_URL = `${API_BASE}/webhooks/${APPLICATION_ID}/${INTERACTION_TOKEN}/messages/@original`;

const rejectAll: Upstream = (request) => {
	throw new Error(`Unexpected request: ${request.method} ${request.url}`);
};

/**
 * Builds an upstream from `"METHOD /path"` routes relative to the Discord
 * API base. A route value may be a Response, a JSON-serialisable object, or a
 * function returning either. Unmatched requests fail the test.
 */
export function discordApi(
	routes: Record<
		string,
		| Response
		| object
		| ((recorded: RecordedRequest) => Response | object | Promise<Response>)
	>,
): Upstream {
	return async (_request, recorded) => {
		const key = `${recorded.method} ${recorded.path}`;
		const route = routes[key];
		if (route === undefined) {
			throw new Error(
				`Unexpected request: ${key}. Known: ${Object.keys(routes).join(", ")}`,
			);
		}
		const result = typeof route === "function" ? await route(recorded) : route;
		return result instanceof Response ? result : Response.json(result);
	};
}

export async function dispatch(
	signer: Signer,
	interaction: APIInteraction,
	upstream: Upstream = rejectAll,
): Promise<Outcome> {
	const requests: RecordedRequest[] = [];
	let edited: ResponseData | undefined;

	vi.stubGlobal(
		"fetch",
		vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
			const request = new Request(input, init);
			const text = await request.clone().text();
			const recorded: RecordedRequest = {
				method: request.method,
				url: request.url,
				path: request.url.startsWith(API_BASE)
					? request.url.slice(API_BASE.length)
					: request.url,
				headers: request.headers,
				body: text ? JSON.parse(text) : undefined,
			};
			if (request.method === "PATCH" && request.url === EDIT_ORIGINAL_URL) {
				expect(edited, "original response edited twice").toBeUndefined();
				edited = recorded.body as ResponseData;
				return Response.json({});
			}
			requests.push(recorded);
			return upstream(request, recorded);
		}),
	);

	try {
		const ctx = createExecutionContext();
		const response = await worker.fetch(
			await signer.sign(serialize(interaction)),
			signer.env,
			ctx,
		);
		const body = (await response.json()) as APIInteractionResponse;
		await waitOnExecutionContext(ctx);
		return { status: response.status, body, edited, requests };
	} finally {
		vi.unstubAllGlobals();
	}
}

/** The single embed of a message-style response or deferred edit. */
export function firstEmbed(
	data: { embeds?: APIEmbed[] | undefined } | undefined,
): APIEmbed {
	const embed = data?.embeds?.[0];
	expect(embed, "response has no embed").toBeDefined();
	return embed as APIEmbed;
}
