import {
	createExecutionContext,
	waitOnExecutionContext,
} from "cloudflare:test";
import { InteractionResponseType } from "discord-api-types/v10";
import { beforeAll, describe, expect, it } from "vitest";

import worker from "../src/server.ts";
import {
	APPLICATION_ID,
	chatInputInteraction,
	createSigner,
	IncomingRequest,
	pingInteraction,
	type Signer,
	serialize,
} from "./helpers.ts";

let signer: Signer;

beforeAll(async () => {
	signer = await createSigner();
});

async function dispatch(request: IncomingRequest) {
	const ctx = createExecutionContext();
	const response = await worker.fetch(request, signer.env, ctx);
	await waitOnExecutionContext(ctx);
	return response;
}

describe("server", () => {
	it("shows the application id on the hello page", async () => {
		const response = await dispatch(
			new IncomingRequest("https://worker.test/"),
		);
		expect(response.status).toBe(200);
		expect(await response.text()).toContain(APPLICATION_ID);
	});

	it("returns 404 for unknown routes", async () => {
		const response = await dispatch(
			new IncomingRequest("https://worker.test/nowhere"),
		);
		expect(response.status).toBe(404);
	});

	it("rejects requests without a signature", async () => {
		const response = await dispatch(
			new IncomingRequest("https://worker.test/", {
				method: "POST",
				body: serialize(pingInteraction()),
			}),
		);
		expect(response.status).toBe(401);
	});

	it("rejects requests signed with the wrong key", async () => {
		const response = await dispatch(
			await signer.forge(serialize(pingInteraction())),
		);
		expect(response.status).toBe(401);
	});

	it("rejects tampered bodies", async () => {
		const signed = await signer.sign(serialize(pingInteraction()));
		const tampered = new IncomingRequest(signed, {
			body: serialize({ ...pingInteraction(), id: "999" }),
		});
		const response = await dispatch(tampered);
		expect(response.status).toBe(401);
	});

	it("answers PING with PONG", async () => {
		const response = await dispatch(
			await signer.sign(serialize(pingInteraction())),
		);
		expect(response.status).toBe(200);
		expect(response.headers.get("content-type")).toContain("application/json");
		expect(await response.json()).toEqual({
			type: InteractionResponseType.Pong,
		});
	});

	it("returns 400 for unknown commands", async () => {
		const response = await dispatch(
			await signer.sign(serialize(chatInputInteraction("does_not_exist"))),
		);
		expect(response.status).toBe(400);
	});
});
