/**
 * Test utilities: an Ed25519 key pair standing in for Discord's, request
 * signing exactly as Discord does it, and interaction payload builders.
 */
import { env as bindings } from "cloudflare:test";
import {
  ApplicationCommandOptionType,
  ApplicationCommandType,
  ComponentType,
  InteractionType,
  type APIApplicationCommandInteractionDataOption,
  type APIChatInputApplicationCommandInteraction,
  type APIEmbed,
  type APIInteraction,
  type APIInteractionDataResolved,
  type APIInteractionDataResolvedGuildMember,
  type APIMessageComponentInteraction,
  type APIPingInteraction,
  type APIUser,
  type APIUserApplicationCommandInteraction,
  type APIUserInteractionDataResolved,
} from "discord-api-types/v10";

import type { Env } from "../src/env.ts";

export const APPLICATION_ID = "966727208586584135";
export const GUILD_ID = "111111111111111111";
export const CHANNEL_ID = "222222222222222222";
export const INVOKER_ID = "333333333333333333";
export const TARGET_ID = "444444444444444444";
export const ROLE_ID = "555555555555555555";
export const INTERACTION_TOKEN = "interaction-token";

/** Requests handed to the worker carry Cloudflare's incoming-request properties. */
export const IncomingRequest = Request<unknown, IncomingRequestCfProperties>;
export type IncomingRequest = Request<unknown, IncomingRequestCfProperties>;

function toHex(bytes: ArrayBuffer): string {
  return Array.from(new Uint8Array(bytes), (byte) =>
    byte.toString(16).padStart(2, "0"),
  ).join("");
}

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
    DB: bindings.DB,
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

// Payload builders.

export interface InteractionOverrides {
  /** Permission bits of the invoking member; defaults to none. */
  permissions?: bigint;
  /** Permission bits of the app in the channel; defaults to none. */
  appPermissions?: bigint;
  /** Roles of the invoking member. */
  roles?: string[];
}

export function user(id: string, username = `user${id.slice(-3)}`): APIUser {
  return {
    id,
    username,
    discriminator: "0",
    global_name: username.charAt(0).toUpperCase() + username.slice(1),
    avatar: null,
  };
}

export function resolvedMember(
  roles: string[] = [],
): APIInteractionDataResolvedGuildMember {
  return {
    roles,
    joined_at: "2024-01-01T00:00:00.000Z",
    flags: 0 as APIInteractionDataResolvedGuildMember["flags"],
    permissions: "0",
  };
}

const BASE = {
  application_id: APPLICATION_ID,
  token: INTERACTION_TOKEN,
  version: 1 as const,
  entitlements: [],
  authorizing_integration_owners: {},
  attachment_size_limit: 0,
};

function guildContext(overrides: InteractionOverrides) {
  return {
    guild_id: GUILD_ID,
    channel_id: CHANNEL_ID,
    app_permissions: (overrides.appPermissions ?? 0n).toString(),
    locale: "uk",
    member: {
      user: user(INVOKER_ID, "invoker"),
      roles: overrides.roles ?? [],
      joined_at: "2024-01-01T00:00:00.000Z",
      deaf: false,
      mute: false,
      flags: 0,
      permissions: (overrides.permissions ?? 0n).toString(),
    },
  };
}

export function pingInteraction(): APIPingInteraction {
  return { ...BASE, id: "1", type: InteractionType.Ping, app_permissions: "0" };
}

/** A slash command invoked inside a guild by INVOKER_ID. */
export function chatInputInteraction(
  name: string,
  options: APIApplicationCommandInteractionDataOption[] = [],
  overrides: InteractionOverrides & {
    resolved?: APIInteractionDataResolved;
  } = {},
): APIChatInputApplicationCommandInteraction {
  const interaction = {
    ...BASE,
    ...guildContext(overrides),
    id: "2",
    type: InteractionType.ApplicationCommand,
    data: {
      id: "3",
      name,
      type: ApplicationCommandType.ChatInput,
      options,
      resolved: overrides.resolved,
    },
  };
  return interaction as unknown as APIChatInputApplicationCommandInteraction;
}

/** A user context-menu command invoked on `target` inside a guild. */
export function userCommandInteraction(
  name: string,
  target: APIUser,
  overrides: InteractionOverrides = {},
): APIUserApplicationCommandInteraction {
  const resolved: APIUserInteractionDataResolved = {
    users: { [target.id]: target },
    members: { [target.id]: resolvedMember() },
  };
  const interaction = {
    ...BASE,
    ...guildContext(overrides),
    id: "4",
    type: InteractionType.ApplicationCommand,
    data: {
      id: "5",
      name,
      type: ApplicationCommandType.User,
      target_id: target.id,
      resolved,
    },
  };
  return interaction as unknown as APIUserApplicationCommandInteraction;
}

/** A button click on a message carrying `embeds`. */
export function buttonInteraction(
  customId: string,
  embeds: APIEmbed[],
  overrides: InteractionOverrides = {},
): APIMessageComponentInteraction {
  const interaction = {
    ...BASE,
    ...guildContext(overrides),
    id: "6",
    type: InteractionType.MessageComponent,
    data: { custom_id: customId, component_type: ComponentType.Button },
    message: {
      id: "7",
      channel_id: CHANNEL_ID,
      author: user(APPLICATION_ID, "traveller"),
      content: "",
      embeds,
      components: [],
    },
  };
  return interaction as unknown as APIMessageComponentInteraction;
}

export function subcommand(
  name: string,
  options: APIApplicationCommandInteractionDataOption[] = [],
): APIApplicationCommandInteractionDataOption {
  return {
    type: ApplicationCommandOptionType.Subcommand,
    name,
    options,
  } as APIApplicationCommandInteractionDataOption;
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

export function roleOption(
  name: string,
  value: string,
): APIApplicationCommandInteractionDataOption {
  return { type: ApplicationCommandOptionType.Role, name, value };
}

export function channelOption(
  name: string,
  value: string,
): APIApplicationCommandInteractionDataOption {
  return { type: ApplicationCommandOptionType.Channel, name, value };
}

export function serialize(interaction: APIInteraction): string {
  return JSON.stringify(interaction);
}
