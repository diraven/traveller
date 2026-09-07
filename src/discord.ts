/**
 * Helpers around the Discord interactions and REST APIs. Anything that
 * touches Discord directly lives here so handlers stay declarative.
 */
import {
	type APIApplicationCommandInteractionDataOption,
	type APIChatInputApplicationCommandInteraction,
	type APIEmbed,
	type APIGuild,
	type APIGuildMember,
	type APIInteraction,
	type APIInteractionDataResolvedGuildMember,
	type APIInteractionResponse,
	type APIInteractionResponseCallbackData,
	type APIMessage,
	type APIMessageComponentInteraction,
	type APIRole,
	type APIUser,
	type APIUserApplicationCommandInteraction,
	ApplicationCommandOptionType,
	InteractionResponseType,
	MessageFlags,
	PermissionFlagsBits,
	type RESTPatchAPIInteractionOriginalResponseJSONBody,
	type RESTPostAPIChannelMessageJSONBody,
} from "discord-api-types/v10";

import type { Env } from "./env.ts";

export const API_BASE = "https://discord.com/api/v10";

/** Embed colors matching discord.py's `discord.Color` presets. */
export const Color = {
	red: 0xe74c3c,
	green: 0x2ecc71,
	blue: 0x3498db,
} as const;

type Handler<Interaction> = (
	interaction: Interaction,
	env: Env,
	ctx: ExecutionContext,
) => Promise<APIInteractionResponse> | APIInteractionResponse;

export type CommandHandler = Handler<APIChatInputApplicationCommandInteraction>;
export type UserCommandHandler = Handler<APIUserApplicationCommandInteraction>;
export type ComponentHandler = Handler<APIMessageComponentInteraction>;

export class JsonResponse extends Response {
	constructor(body: unknown, init?: ResponseInit) {
		super(JSON.stringify(body), {
			...init,
			headers: {
				"content-type": "application/json;charset=UTF-8",
				...init?.headers,
			},
		});
	}
}

// Responses.

export function message(
	data: APIInteractionResponseCallbackData,
): APIInteractionResponse {
	return { type: InteractionResponseType.ChannelMessageWithSource, data };
}

export function embedMessage(embed: APIEmbed): APIInteractionResponse {
	return message({ embeds: [embed] });
}

export function updateMessage(
	data: APIInteractionResponseCallbackData,
): APIInteractionResponse {
	return { type: InteractionResponseType.UpdateMessage, data };
}

export function errorEmbed(title: string, description: string): APIEmbed {
	return { title, description, color: Color.red };
}

export function successEmbed(title: string, description: string): APIEmbed {
	return { title, description, color: Color.green };
}

export function ephemeralError(
	title: string,
	description: string,
): APIInteractionResponse {
	return message({
		embeds: [errorEmbed(title, description)],
		flags: MessageFlags.Ephemeral,
	});
}

export const NO_ACCESS = ephemeralError("Помилка", "Відсутній доступ.");

/**
 * Discord requires an answer within 3 seconds. Handlers that call external
 * services acknowledge immediately and finish the work in the background,
 * then edit the original response.
 */
export function deferred(
	interaction: APIInteraction,
	env: Env,
	ctx: ExecutionContext,
	work: () => Promise<APIInteractionResponseCallbackData>,
): APIInteractionResponse {
	finishInBackground(interaction, env, ctx, work);
	return { type: InteractionResponseType.DeferredChannelMessageWithSource };
}

/**
 * Same, for a button click that edits the message the button sits on. The
 * user sees no loading state, so the message simply updates a moment later.
 */
export function deferredUpdate(
	interaction: APIInteraction,
	env: Env,
	ctx: ExecutionContext,
	work: () => Promise<APIInteractionResponseCallbackData>,
): APIInteractionResponse {
	finishInBackground(interaction, env, ctx, work);
	return { type: InteractionResponseType.DeferredMessageUpdate };
}

function finishInBackground(
	interaction: APIInteraction,
	env: Env,
	ctx: ExecutionContext,
	work: () => Promise<APIInteractionResponseCallbackData>,
): void {
	ctx.waitUntil(
		work()
			.catch((error: unknown) => {
				console.error(error);
				return { embeds: [errorEmbed("Помилка", userFacingMessage(error))] };
			})
			.then((data) => editOriginalResponse(env, interaction.token, data))
			.catch((error: unknown) => {
				console.error(error);
			}),
	);
}

/** Keeps internal detail such as request paths out of public channels. */
export function userFacingMessage(error: unknown): string {
	if (error instanceof DiscordAPIError) {
		return `Discord відповів помилкою ${error.status}.`;
	}
	return "Спробуйте ще раз пізніше.";
}

export async function editOriginalResponse(
	env: Env,
	interactionToken: string,
	data: RESTPatchAPIInteractionOriginalResponseJSONBody,
): Promise<void> {
	const url = `${API_BASE}/webhooks/${env.DISCORD_APPLICATION_ID}/${interactionToken}/messages/@original`;
	const response = await fetch(url, {
		method: "PATCH",
		headers: { "content-type": "application/json" },
		body: JSON.stringify(data),
	});
	if (!response.ok) {
		throw new Error(
			`Failed to edit original response: ${response.status} ${await response.text()}`,
		);
	}
}

// Interaction payload accessors.

/** Options of the invoked (sub)command, unwrapping a subcommand if present. */
export function getOptions(
	interaction: APIChatInputApplicationCommandInteraction,
): APIApplicationCommandInteractionDataOption[] {
	const options = interaction.data.options ?? [];
	const first = options[0];
	if (first?.type === ApplicationCommandOptionType.Subcommand) {
		return first.options ?? [];
	}
	return options;
}

export function getSubcommandName(
	interaction: APIChatInputApplicationCommandInteraction,
): string | undefined {
	const option = interaction.data.options?.[0];
	return option?.type === ApplicationCommandOptionType.Subcommand
		? option.name
		: undefined;
}

function findOption(
	interaction: APIChatInputApplicationCommandInteraction,
	name: string,
	type: ApplicationCommandOptionType,
): APIApplicationCommandInteractionDataOption | undefined {
	const option = getOptions(interaction).find(
		(candidate) => candidate.name === name,
	);
	return option?.type === type ? option : undefined;
}

function requireOption(
	interaction: APIChatInputApplicationCommandInteraction,
	name: string,
	type: ApplicationCommandOptionType,
): APIApplicationCommandInteractionDataOption {
	const option = findOption(interaction, name, type);
	if (!option) {
		throw new Error(`Missing option "${name}".`);
	}
	return option;
}

export function getOptionalStringOption(
	interaction: APIChatInputApplicationCommandInteraction,
	name: string,
): string | undefined {
	const option = findOption(
		interaction,
		name,
		ApplicationCommandOptionType.String,
	);
	return option?.type === ApplicationCommandOptionType.String
		? option.value
		: undefined;
}

export function getStringOption(
	interaction: APIChatInputApplicationCommandInteraction,
	name: string,
): string {
	const option = requireOption(
		interaction,
		name,
		ApplicationCommandOptionType.String,
	);
	return option.type === ApplicationCommandOptionType.String
		? option.value
		: "";
}

/** Returns the snowflake chosen in a user, role or channel option. */
function getSnowflakeOption(
	interaction: APIChatInputApplicationCommandInteraction,
	name: string,
	type:
		| ApplicationCommandOptionType.User
		| ApplicationCommandOptionType.Role
		| ApplicationCommandOptionType.Channel,
): string {
	const option = requireOption(interaction, name, type);
	return "value" in option ? String(option.value) : "";
}

export function getUserOption(
	interaction: APIChatInputApplicationCommandInteraction,
	name: string,
): string {
	return getSnowflakeOption(
		interaction,
		name,
		ApplicationCommandOptionType.User,
	);
}

export function getRoleOption(
	interaction: APIChatInputApplicationCommandInteraction,
	name: string,
): string {
	return getSnowflakeOption(
		interaction,
		name,
		ApplicationCommandOptionType.Role,
	);
}

export function getChannelOption(
	interaction: APIChatInputApplicationCommandInteraction,
	name: string,
): string {
	return getSnowflakeOption(
		interaction,
		name,
		ApplicationCommandOptionType.Channel,
	);
}

export function getResolvedUser(
	interaction:
		| APIChatInputApplicationCommandInteraction
		| APIUserApplicationCommandInteraction,
	userId: string,
): APIUser | undefined {
	return interaction.data.resolved?.users?.[userId];
}

export function getResolvedMember(
	interaction:
		| APIChatInputApplicationCommandInteraction
		| APIUserApplicationCommandInteraction,
	userId: string,
): APIInteractionDataResolvedGuildMember | undefined {
	return interaction.data.resolved?.members?.[userId];
}

export function getInvoker(interaction: APIInteraction): APIUser {
	const user = interaction.member?.user ?? interaction.user;
	if (!user) {
		throw new Error("Interaction has no user.");
	}
	return user;
}

export function getGuildId(interaction: APIInteraction): string {
	if (!interaction.guild_id) {
		throw new Error("Interaction is not from a guild.");
	}
	return interaction.guild_id;
}

// Permissions.

export function hasPermission(
	permissions: string | null | undefined,
	flag: bigint,
): boolean {
	if (!permissions) {
		return false;
	}
	const bits = BigInt(permissions);
	return (
		(bits & PermissionFlagsBits.Administrator) ===
			PermissionFlagsBits.Administrator || (bits & flag) === flag
	);
}

/** Whether the invoking member holds `flag` in the interaction's channel. */
export function memberHasPermission(
	interaction: APIInteraction,
	flag: bigint,
): boolean {
	return hasPermission(interaction.member?.permissions, flag);
}

/** Whether the app itself holds `flag` in the interaction's channel. */
export function appHasPermission(
	interaction: APIInteraction,
	flag: bigint,
): boolean {
	return hasPermission(interaction.app_permissions, flag);
}

// Formatting.

export function userMention(userId: string): string {
	return `<@${userId}>`;
}

export function roleMention(roleId: string): string {
	return `<@&${roleId}>`;
}

export function channelMention(channelId: string): string {
	return `<#${channelId}>`;
}

export function displayName(user: APIUser): string {
	return user.global_name ?? user.username;
}

export function avatarUrl(user: APIUser): string | undefined {
	return user.avatar
		? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`
		: undefined;
}

export function truncate(text: string, maxLength: number): string {
	return text.length < maxLength ? text : `${text.slice(0, maxLength)}...`;
}

// REST API.

export class DiscordAPIError extends Error {
	readonly status: number;
	readonly path: string;
	readonly body: string;

	constructor(status: number, path: string, body: string) {
		super(`Discord API ${status} on ${path}: ${body}`);
		this.name = "DiscordAPIError";
		this.status = status;
		this.path = path;
		this.body = body;
	}
}

export async function discordRequest<T>(
	env: Env,
	method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
	path: string,
	body?: unknown,
	auditLogReason?: string,
): Promise<T> {
	const headers: Record<string, string> = {
		authorization: `Bot ${env.DISCORD_TOKEN}`,
	};
	if (body !== undefined) {
		headers["content-type"] = "application/json";
	}
	if (auditLogReason) {
		headers["x-audit-log-reason"] = encodeURIComponent(auditLogReason);
	}
	const response = await fetch(`${API_BASE}${path}`, {
		method,
		headers,
		...(body !== undefined && { body: JSON.stringify(body) }),
	});
	if (!response.ok) {
		throw new DiscordAPIError(response.status, path, await response.text());
	}
	if (response.status === 204) {
		return undefined as T;
	}
	return (await response.json()) as T;
}

export function createMessage(
	env: Env,
	channelId: string,
	body: RESTPostAPIChannelMessageJSONBody,
): Promise<APIMessage> {
	return discordRequest(env, "POST", `/channels/${channelId}/messages`, body);
}

/** Whether `userId` is banned on `guildId`; the API 404s when they are not. */
export async function isBanned(
	env: Env,
	guildId: string,
	userId: string,
): Promise<boolean> {
	try {
		await discordRequest(env, "GET", `/guilds/${guildId}/bans/${userId}`);
		return true;
	} catch (error) {
		if (error instanceof DiscordAPIError && error.status === 404) {
			return false;
		}
		throw error;
	}
}

export function banMember(
	env: Env,
	guildId: string,
	userId: string,
	reason?: string,
): Promise<void> {
	return discordRequest(
		env,
		"PUT",
		`/guilds/${guildId}/bans/${userId}`,
		{},
		reason,
	);
}

export function addMemberRole(
	env: Env,
	guildId: string,
	userId: string,
	roleId: string,
	reason?: string,
): Promise<void> {
	return discordRequest(
		env,
		"PUT",
		`/guilds/${guildId}/members/${userId}/roles/${roleId}`,
		undefined,
		reason,
	);
}

export function getGuild(env: Env, guildId: string): Promise<APIGuild> {
	return discordRequest(env, "GET", `/guilds/${guildId}`);
}

export function getGuildRoles(env: Env, guildId: string): Promise<APIRole[]> {
	return discordRequest(env, "GET", `/guilds/${guildId}/roles`);
}

export function getGuildMember(
	env: Env,
	guildId: string,
	userId: string,
): Promise<APIGuildMember> {
	return discordRequest(env, "GET", `/guilds/${guildId}/members/${userId}`);
}

/**
 * The app's guild-wide permissions in every guild it is in, keyed by guild
 * id. Unlike `app_permissions` on an interaction these ignore per-channel
 * overwrites, which is what "can the bot ban here at all" needs.
 */
export async function getAppGuildPermissions(
	env: Env,
): Promise<Map<string, bigint>> {
	const permissions = new Map<string, bigint>();
	let after: string | undefined;

	// Paginated at 200 guilds per page.
	for (;;) {
		const query = new URLSearchParams({ limit: "200" });
		if (after) {
			query.set("after", after);
		}
		const page = await discordRequest<{ id: string; permissions: string }[]>(
			env,
			"GET",
			`/users/@me/guilds?${query.toString()}`,
		);
		for (const guild of page) {
			permissions.set(guild.id, BigInt(guild.permissions));
		}
		if (page.length < 200) {
			return permissions;
		}
		after = page[page.length - 1]?.id;
	}
}
