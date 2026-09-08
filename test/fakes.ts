/**
 * Stand-ins for the discord.js objects handlers touch.
 *
 * Handlers reply through the interaction rather than returning a payload, so
 * tests assert on what was sent: every fake records its calls with `vi.fn()`.
 * The casts are deliberate - a fake only implements the slice of the discord.js
 * surface the code under test actually uses.
 */
import {
	type APIEmbed,
	type ButtonInteraction,
	type ChatInputCommandInteraction,
	type Client,
	DiscordAPIError,
	type Guild,
	RESTJSONErrorCodes,
	type User,
} from "discord.js";
import { vi } from "vitest";

import type { Queryable } from "../src/db.ts";

export interface FakeUser {
	id: string;
	username: string;
	displayName: string;
	avatarURL: () => string | null;
}

export function fakeUser(overrides: Partial<FakeUser> = {}): FakeUser {
	const id = overrides.id ?? "100";
	return {
		id,
		username: overrides.username ?? `user${id}`,
		displayName: overrides.displayName ?? `User ${id}`,
		avatarURL: overrides.avatarURL ?? (() => null),
	};
}

export interface FakeMember {
	roles: { cache: Set<string>; add: ReturnType<typeof vi.fn> };
}

export function fakeMember(roles: string[] = []): FakeMember {
	return { roles: { cache: new Set(roles), add: vi.fn() } };
}

export interface FakeMessage {
	id: string;
	reply: ReturnType<typeof vi.fn>;
	edit: ReturnType<typeof vi.fn>;
}

export function fakeMessage(id = "msg1"): FakeMessage {
	return { id, reply: vi.fn(), edit: vi.fn() };
}

export interface FakeChannel {
	id: string;
	sendable: boolean;
	/** The message `send` resolves to, so tests can assert on its replies. */
	message: FakeMessage;
	send: ReturnType<typeof vi.fn>;
	isSendable: () => boolean;
	isTextBased: () => boolean;
}

export function fakeChannel(id = "chan1", sendable = true): FakeChannel {
	const message = fakeMessage();
	return {
		id,
		sendable,
		message,
		send: vi.fn(async () => message),
		isSendable: () => sendable,
		isTextBased: () => true,
	};
}

export interface FakeGuildOptions {
	id?: string;
	name?: string;
	channel?: FakeChannel;
	/** Permissions the bot itself holds guild-wide. */
	mePermissions?: bigint[];
	/** Highest role position the bot holds, for the verification checks. */
	meTopRole?: number;
	roles?: { id: string; position: number }[];
	/** User ids that are banned; `bans.fetch` rejects for anything else. */
	bans?: string[];
}

export function fakeGuild(options: FakeGuildOptions = {}) {
	const channel = options.channel ?? fakeChannel();
	const banned = new Set(options.bans ?? []);
	const permissions = options.mePermissions ?? [];

	return {
		id: options.id ?? "guild1",
		name: options.name ?? "Test Guild",
		channel,
		channels: { fetch: vi.fn(async () => channel) },
		roles: {
			fetch: vi.fn(
				async (id: string) =>
					options.roles?.find((role) => role.id === id) ?? null,
			),
		},
		members: {
			fetchMe: vi.fn(async () => ({
				permissions: { has: (flag: bigint) => permissions.includes(flag) },
				roles: { highest: { position: options.meTopRole ?? 10 } },
			})),
		},
		bans: {
			fetch: vi.fn(async (id: string) => {
				if (!banned.has(id)) {
					throw unknownBanError();
				}
				return { user: fakeUser({ id }) };
			}),
			create: vi.fn(async () => undefined),
		},
	};
}

/** The error Discord returns from `GET /guilds/{id}/bans/{user}` when absent. */
export function unknownBanError(): Error {
	return new DiscordAPIError(
		{ code: RESTJSONErrorCodes.UnknownBan, message: "Unknown Ban" },
		RESTJSONErrorCodes.UnknownBan,
		404,
		"GET",
		"/bans",
		{},
	);
}

export interface FakeInteractionOptions {
	commandName?: string;
	subcommand?: string;
	strings?: Record<string, string>;
	users?: Record<string, FakeUser>;
	roles?: Record<string, { id: string }>;
	channels?: Record<string, { id: string }>;
	members?: Record<string, FakeMember | null>;
	/** Permissions the invoking member holds. */
	permissions?: bigint[];
	/** Roles the invoking member holds. */
	memberRoles?: string[];
	user?: FakeUser;
	guild?: ReturnType<typeof fakeGuild>;
	client?: FakeClient;
}

export function fakeInteraction(options: FakeInteractionOptions = {}) {
	const guild = options.guild ?? fakeGuild();
	const user = options.user ?? fakeUser({ id: "1" });
	const permissions = options.permissions ?? [];
	const memberRoles = new Set(options.memberRoles ?? []);

	return {
		commandName: options.commandName ?? "test",
		guild,
		guildId: guild.id,
		user,
		client: options.client ?? fakeClient(),
		member: { roles: { cache: memberRoles } },
		memberPermissions: {
			has: (flag: bigint) => permissions.includes(flag),
		},
		options: {
			getSubcommand: () => options.subcommand ?? "",
			getString: (name: string, required?: boolean) => {
				const value = options.strings?.[name] ?? null;
				if (!value && required) {
					throw new Error(`Missing required string option ${name}.`);
				}
				return value;
			},
			getUser: (name: string, required?: boolean) => {
				const value = options.users?.[name] ?? null;
				if (!value && required) {
					throw new Error(`Missing required user option ${name}.`);
				}
				return value;
			},
			getRole: (name: string, _required?: boolean) =>
				options.roles?.[name] ?? null,
			getChannel: (name: string, _required?: boolean) =>
				options.channels?.[name] ?? null,
			getMember: (name: string) => options.members?.[name] ?? null,
		},
		deferred: false,
		replied: false,
		reply: vi.fn(),
		deferReply: vi.fn(),
		editReply: vi.fn(),
		update: vi.fn(),
		deferUpdate: vi.fn(),
		followUp: vi.fn(),
	};
}

export interface FakeButtonOptions extends FakeInteractionOptions {
	customId?: string;
	embed?: APIEmbed;
}

export function fakeButtonInteraction(options: FakeButtonOptions = {}) {
	const base = fakeInteraction(options);
	return {
		...base,
		customId: options.customId ?? "button",
		message: {
			embeds: options.embed
				? [{ toJSON: () => options.embed as APIEmbed }]
				: [],
		},
	};
}

export interface FakeClient {
	user: { id: string };
	users: { fetch: ReturnType<typeof vi.fn> };
	guilds: {
		cache: Map<string, unknown>;
		fetch: ReturnType<typeof vi.fn>;
	};
}

export function fakeClient(
	users: FakeUser[] = [],
	guilds: ReturnType<typeof fakeGuild>[] = [],
): FakeClient {
	const byId = new Map(users.map((user) => [user.id, user]));
	const guildsById = new Map(guilds.map((guild) => [guild.id, guild]));
	return {
		user: { id: "bot" },
		users: {
			fetch: vi.fn(async (id: string) => {
				const found = byId.get(id);
				if (!found) {
					throw new Error(`Unknown user ${id}`);
				}
				return found;
			}),
		},
		guilds: {
			cache: guildsById as Map<string, unknown>,
			fetch: vi.fn(async (id: string) => {
				const found = guildsById.get(id);
				if (!found) {
					throw new Error(`Unknown guild ${id}`);
				}
				return found;
			}),
		},
	};
}

/** A Queryable backed by canned responses, keyed by a substring of the SQL. */
export function fakeDb(
	responses: { match: string; rows?: unknown[]; rowCount?: number }[],
): Queryable & { queries: { sql: string; values: unknown[] }[] } {
	const queries: { sql: string; values: unknown[] }[] = [];
	const query = vi.fn(async (sql: string, values: unknown[] = []) => {
		queries.push({ sql, values });
		const canned = responses.find((response) => sql.includes(response.match));
		const rows = canned?.rows ?? [];
		return { rows, rowCount: canned?.rowCount ?? rows.length };
	});
	return Object.assign({ query }, { queries }) as unknown as Queryable & {
		queries: { sql: string; values: unknown[] }[];
	};
}

// Casts used at the call sites, kept here so the tests stay readable.
export const asCommand = (fake: unknown) =>
	fake as unknown as ChatInputCommandInteraction<"cached">;
export const asButton = (fake: unknown) =>
	fake as unknown as ButtonInteraction<"cached">;
export const asClient = (fake: unknown) => fake as unknown as Client;
export const asGuild = (fake: unknown) => fake as unknown as Guild;
export const asUser = (fake: unknown) => fake as unknown as User;
