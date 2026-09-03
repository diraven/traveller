/**
 * Test utilities: an Ed25519 key pair standing in for Discord's, request
 * signing exactly as Discord does it, and interaction payload builders.
 */
import {
  ApplicationCommandOptionType,
  ApplicationCommandType,
  InteractionType,
  type APIApplicationCommandInteractionDataOption,
  type APIChatInputApplicationCommandInteraction,
  type APIInteraction,
  type APIPingInteraction,
} from "discord-api-types/v10";

import type { Env } from "../src/env.ts";

export const APPLICATION_ID = "966727208586584135";
export const GUILD_ID = "111111111111111111";
export const CHANNEL_ID = "222222222222222222";
export const INVOKER_ID = "333333333333333333";
export const TARGET_ID = "444444444444444444";
export const INTERACTION_TOKEN = "interaction-token";

/** Requests handed to the worker carry Cloudflare's incoming-request properties. */
export const IncomingRequest = Request<unknown, IncomingRequestCfProperties>;

function toHex(bytes: ArrayBuffer): string {
  return Array.from(new Uint8Array(bytes), (byte) =>
    byte.toString(16).padStart(2, "0"),
  ).join("");
}

export type IncomingRequest = Request<unknown, IncomingRequestCfProperties>;

export interface Signer {
  env: Env;
  sign(body: string, timestamp?: string): Promise<IncomingRequest>;
  forge(body: string): Promise<IncomingRequest>;
}

/** Generates a fresh key pair and an Env whose public key matches it. */
export async function createSigner(): Promise<Signer> {
  const keyPair = (await crypto.subtle.generateKey({ name: "Ed25519" }, true, [
    "sign",
    "verify",
  ])) as CryptoKeyPair;
  const publicKey = toHex(
    (await crypto.subtle.exportKey("raw", keyPair.publicKey)) as ArrayBuffer,
  );
  const env: Env = {
    DISCORD_APPLICATION_ID: APPLICATION_ID,
    DISCORD_PUBLIC_KEY: publicKey,
    DISCORD_TOKEN: "bot-token",
  };

  async function request(
    body: string,
    timestamp: string,
    signingKey: CryptoKey,
  ): Promise<IncomingRequest> {
    const signature = await crypto.subtle.sign(
      "Ed25519",
      signingKey,
      new TextEncoder().encode(timestamp + body),
    );
    return new IncomingRequest("https://worker.test/", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-signature-ed25519": toHex(signature),
        "x-signature-timestamp": timestamp,
      },
      body,
    });
  }

  return {
    env,
    sign: (body, timestamp = String(Math.floor(Date.now() / 1000))) =>
      request(body, timestamp, keyPair.privateKey),
    async forge(body) {
      const other = (await crypto.subtle.generateKey(
        { name: "Ed25519" },
        true,
        ["sign", "verify"],
      )) as CryptoKeyPair;
      return request(
        body,
        String(Math.floor(Date.now() / 1000)),
        other.privateKey,
      );
    },
  };
}

export function pingInteraction(): APIPingInteraction {
  return {
    id: "1",
    application_id: APPLICATION_ID,
    type: InteractionType.Ping,
    token: INTERACTION_TOKEN,
    version: 1,
    app_permissions: "0",
    entitlements: [],
    authorizing_integration_owners: {},
    attachment_size_limit: 0,
  };
}

/** A slash command invoked inside a guild by INVOKER_ID. */
export function chatInputInteraction(
  name: string,
  options: APIApplicationCommandInteractionDataOption[] = [],
): APIChatInputApplicationCommandInteraction {
  const interaction = {
    id: "2",
    application_id: APPLICATION_ID,
    type: InteractionType.ApplicationCommand,
    token: INTERACTION_TOKEN,
    version: 1,
    guild_id: GUILD_ID,
    channel_id: CHANNEL_ID,
    app_permissions: "0",
    entitlements: [],
    authorizing_integration_owners: {},
    attachment_size_limit: 0,
    locale: "uk",
    member: {
      user: {
        id: INVOKER_ID,
        username: "invoker",
        discriminator: "0",
        global_name: "Invoker",
        avatar: null,
      },
      roles: [],
      joined_at: "2024-01-01T00:00:00.000Z",
      deaf: false,
      mute: false,
      flags: 0,
      permissions: "0",
    },
    data: {
      id: "3",
      name,
      type: ApplicationCommandType.ChatInput,
      options,
    },
  };
  return interaction as unknown as APIChatInputApplicationCommandInteraction;
}

export function subcommand(
  name: string,
): APIApplicationCommandInteractionDataOption {
  return { type: ApplicationCommandOptionType.Subcommand, name, options: [] };
}

export function stringOption(
  name: string,
  value: string,
): APIApplicationCommandInteractionDataOption {
  return { type: ApplicationCommandOptionType.String, name, value };
}

export function userOption(
  name: string,
  value: string,
): APIApplicationCommandInteractionDataOption {
  return { type: ApplicationCommandOptionType.User, name, value };
}

export function serialize(interaction: APIInteraction): string {
  return JSON.stringify(interaction);
}
