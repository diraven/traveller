/**
 * Command definitions shared by the runtime router and the registration
 * script, so the two can never drift apart.
 */
import {
	ApplicationCommandOptionType,
	ApplicationCommandType,
	ApplicationIntegrationType,
	ChannelType,
	InteractionContextType,
	PermissionFlagsBits,
	type RESTPostAPIApplicationCommandsJSONBody,
	type RESTPostAPIChatInputApplicationCommandsJSONBody,
	type RESTPostAPIContextMenuApplicationCommandsJSONBody,
} from "discord.js";

import { FAQ_ENTRIES } from "./faq_entries.ts";

/** Every command is installed on servers only and usable inside servers only. */
const GUILD_ONLY: Pick<
	RESTPostAPIApplicationCommandsJSONBody,
	"integration_types" | "contexts"
> = {
	integration_types: [ApplicationIntegrationType.GuildInstall],
	contexts: [InteractionContextType.Guild],
};

const CHAT_INPUT: Pick<
	RESTPostAPIChatInputApplicationCommandsJSONBody,
	"type" | "integration_types" | "contexts"
> = { ...GUILD_ONLY, type: ApplicationCommandType.ChatInput };

export const FAQ_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody = {
	...CHAT_INPUT,
	name: "faq",
	description: "ЧаПи",
	options: Object.entries(FAQ_ENTRIES).map(([name, entry]) => ({
		type: ApplicationCommandOptionType.Subcommand,
		name,
		description: entry.title,
	})),
};

export const SLAP_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody = {
	...CHAT_INPUT,
	name: "slap",
	description: "Йой!",
	options: [
		{
			type: ApplicationCommandOptionType.User,
			name: "member",
			description: "Кого",
			required: true,
		},
	],
};

export const RUSNI_PYZDA_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody =
	{
		...CHAT_INPUT,
		name: "rusni_pyzda",
		description: "Втрати РФ станом на сьогодні.",
	};

export const VERIFICATION_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody =
	{
		...CHAT_INPUT,
		name: "verification",
		description: "Верифікація",
		default_member_permissions: PermissionFlagsBits.Administrator.toString(),
		options: [
			{
				type: ApplicationCommandOptionType.Subcommand,
				name: "set_role",
				description: "Налаштувати роль верифікації",
				options: [
					{
						type: ApplicationCommandOptionType.Role,
						name: "role",
						description: "Роль, яку отримують верифіковані учасники",
						required: true,
					},
				],
			},
			{
				type: ApplicationCommandOptionType.Subcommand,
				name: "check_config",
				description: "Перевірити налаштування верифікації",
			},
		],
	};

export const VERIFY_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody = {
	...CHAT_INPUT,
	name: "verify",
	description: "Верифікувати користувача",
	options: [
		{
			type: ApplicationCommandOptionType.User,
			name: "member",
			description: "Кого верифікувати",
			required: true,
		},
	],
};

export const BANS_SHARING_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody =
	{
		...CHAT_INPUT,
		name: "bans_sharing",
		description: "Шаринг банів",
		default_member_permissions: PermissionFlagsBits.BanMembers.toString(),
		options: [
			{
				type: ApplicationCommandOptionType.Subcommand,
				name: "share",
				description: "Поширити бан на інші сервери",
				options: [
					{
						type: ApplicationCommandOptionType.User,
						name: "user",
						description: "Забанений користувач",
						required: true,
					},
					{
						type: ApplicationCommandOptionType.String,
						name: "reason",
						description: "Причина бану",
						max_length: 500,
					},
				],
			},
			{
				type: ApplicationCommandOptionType.Subcommand,
				name: "set_channel",
				description: "Налаштувати канал сповіщень",
				options: [
					{
						type: ApplicationCommandOptionType.Channel,
						name: "channel",
						description: "Канал для сповіщень про бани",
						channel_types: [ChannelType.GuildText],
						required: true,
					},
				],
			},
			{
				type: ApplicationCommandOptionType.Subcommand,
				name: "check_config",
				description: "Перевірити налаштування шарингу банів",
			},
			// A snowflake rather than a user option: the moderator being trusted is
			// by definition from another server, and a user picker only lists
			// members of this one.
			{
				type: ApplicationCommandOptionType.Subcommand,
				name: "add_trusted_moderator",
				description: "Зробити модератора довіреним",
				options: [
					{
						type: ApplicationCommandOptionType.String,
						name: "user_id",
						description: "Ідентифікатор модератора з іншого сервера",
						required: true,
					},
				],
			},
			{
				type: ApplicationCommandOptionType.Subcommand,
				name: "remove_trusted_moderator",
				description: "Прибрати модератора з довірених",
				options: [
					{
						type: ApplicationCommandOptionType.String,
						name: "user_id",
						description: "Ідентифікатор модератора з іншого сервера",
						required: true,
					},
				],
			},
		],
	};

/** Right-click a user, "Apps", share their ban. Same as `/bans_sharing share`. */
export const SHARE_BAN_USER_COMMAND: RESTPostAPIContextMenuApplicationCommandsJSONBody =
	{
		...GUILD_ONLY,
		type: ApplicationCommandType.User,
		name: "Поширити бан",
		default_member_permissions: PermissionFlagsBits.BanMembers.toString(),
	};

export const COMMANDS: RESTPostAPIApplicationCommandsJSONBody[] = [
	FAQ_COMMAND,
	SLAP_COMMAND,
	RUSNI_PYZDA_COMMAND,
	VERIFICATION_COMMAND,
	VERIFY_COMMAND,
	BANS_SHARING_COMMAND,
	SHARE_BAN_USER_COMMAND,
];
