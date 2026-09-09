/**
 * Bans sharing across servers.
 *
 * The bot watches each server's audit log and offers to pass new bans on (see
 * confirm.ts). `/bans_sharing share` and the "Поширити бан" context menu do the
 * same thing on demand, for bans that happened while the bot was away or that
 * were skipped earlier.
 *
 * On the receiving side moderators get "ban too" and "ignore" buttons, or the
 * ban is applied automatically when it came from a trusted moderator.
 */
import {
	channelMention,
	DiscordAPIError,
	PermissionFlagsBits,
	RESTJSONErrorCodes,
	userMention,
} from "discord.js";

import type {
	ButtonHandler,
	CommandHandler,
	Context,
	UserCommandHandler,
} from "../../context.ts";
import * as db from "../../db.ts";
import {
	Color,
	ephemeralError,
	errorEmbed,
	fetchSendableChannel,
	isSnowflake,
	NO_ACCESS,
	successEmbed,
	userFacingMessage,
} from "../../discord.ts";
import {
	BAN_BUTTON_ID,
	BANNED_FIELD,
	type Ban,
	banButtons,
	banEmbed,
	embedField,
	embedReason,
	fanOut,
	SKIP_BUTTON_ID,
	TARGET_ID_FIELD,
} from "./share.ts";

export {
	NO_SHARE_BUTTON_ID,
	noShareButton,
	onAuditLogEntry,
	SHARE_BUTTON_ID,
	shareButton,
} from "./confirm.ts";
export { BAN_BUTTON_ID, SKIP_BUTTON_ID };

/**
 * One record per banned user is kept network-wide, and it is written when the
 * ban is first noticed - not when it is actually passed on. So "handled" is the
 * honest word here: the ban may have been shared, declined, or left to expire.
 */
const ALREADY_HANDLED = "Бан вже опрацьовано";

function handledText(targetId: string): string {
	return `Бан користувача ${userMention(targetId)} вже опрацьовано раніше.`;
}

function notFound(userId: string) {
	return errorEmbed(
		"Користувача не знайдено",
		`Користувач з ідентифікатором ${userId}, не знайдений.`,
	);
}

/**
 * Shares a ban on demand. Unlike the audit log path this cannot assume the ban
 * is real, so it checks with Discord first: servers that trust the moderator
 * apply it automatically.
 */
async function shareOnDemand(
	interaction:
		| Parameters<CommandHandler>[0]
		| Parameters<UserCommandHandler>[0],
	ctx: Context,
	target: Parameters<CommandHandler>[0]["user"],
	reason: string | undefined,
): Promise<void> {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.BanMembers)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	const { guild } = interaction;

	const stored = await db.getGuild(ctx.db, guild.id);
	if (!stored?.bans_sharing_channel_id) {
		await interaction.reply(
			ephemeralError(
				"Не налаштовано канал сповіщень.",
				"Налаштуйте канал сповіщень за допомогою команди `/bans_sharing set_channel`.",
			),
		);
		return;
	}
	// A cheap upfront answer for the common case. The claim below is what
	// actually prevents a double share.
	if (await db.hasSeenBan(ctx.db, target.id)) {
		await interaction.reply(
			ephemeralError(ALREADY_HANDLED, handledText(target.id)),
		);
		return;
	}

	await interaction.deferReply();

	try {
		await guild.bans.fetch(target.id);
	} catch (error) {
		if (
			error instanceof DiscordAPIError &&
			error.code === RESTJSONErrorCodes.UnknownBan
		) {
			await interaction.editReply({
				embeds: [
					errorEmbed(
						"Користувача не забанено",
						`${userMention(target.id)} не забанений на цьому сервері. Спочатку забаньте його, потім поширюйте бан.`,
					),
				],
			});
			return;
		}
		throw error;
	}

	// Claimed before the fan-out, so two moderators sharing the same ban at the
	// same moment cannot both notify every server.
	if (!(await db.claimBan(ctx.db, target.id, interaction.user.id, reason))) {
		await interaction.editReply({
			embeds: [errorEmbed(ALREADY_HANDLED, handledText(target.id))],
		});
		return;
	}

	const ban: Ban = {
		guildId: guild.id,
		guildName: guild.name,
		actor: interaction.user,
		target,
		reason,
	};
	let delivered: number;
	let total: number;
	try {
		({ delivered, total } = await fanOut(interaction.client, ctx.db, ban));
	} catch (error) {
		// fanOut absorbs per-server failures, so this is something unexpected.
		// Release the claim rather than marking the ban seen for good.
		await db.releaseBan(ctx.db, target.id);
		throw error;
	}

	// Local notice, so the originating server keeps a record too.
	const local = banEmbed(ban);
	local.title = "Новий бан на цьому сервері";
	local.description = `**Статус:** поширено на ${delivered} з ${total} серверів модератором ${userMention(interaction.user.id)}`;
	const channel = await fetchSendableChannel(
		guild,
		stored.bans_sharing_channel_id,
	);
	if (channel) {
		const content = embedField(local, BANNED_FIELD);
		try {
			await channel.send({ ...(content && { content }), embeds: [local] });
		} catch (error) {
			// The fan-out already happened; the local copy is a convenience.
			console.error(error);
		}
	}

	await interaction.editReply({
		embeds: [
			successEmbed(
				"Бан поширено",
				`Сповіщення про бан ${userMention(target.id)} відправлено на ${delivered} з ${total} серверів.`,
			),
		],
	});
}

const share: CommandHandler = (interaction, ctx) =>
	shareOnDemand(
		interaction,
		ctx,
		interaction.options.getUser("user", true),
		interaction.options.getString("reason") ?? undefined,
	);

export const shareBanUserCommand: UserCommandHandler = (interaction, ctx) =>
	shareOnDemand(interaction, ctx, interaction.targetUser, undefined);

const setChannel: CommandHandler = async (interaction, ctx) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.Administrator)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	const channel = interaction.options.getChannel("channel", true);
	await interaction.deferReply();

	const noAccess = errorEmbed(
		"Відсутній доступ",
		`Відсутній доступ до каналу сповіщень ${channelMention(channel.id)}, перевірте налаштування ролей.`,
	);
	const resolved = await fetchSendableChannel(interaction.guild, channel.id);
	if (!resolved) {
		await interaction.editReply({ embeds: [noAccess] });
		return;
	}
	// isSendable only checks the channel type, so the test message below is what
	// actually proves the bot can post there.
	try {
		await resolved.send({
			embeds: [
				{
					title: "Перевірка",
					description: `Тестове повідомлення для перевірки доступу до каналу сповіщень ${channelMention(channel.id)}.`,
				},
			],
		});
	} catch (error) {
		if (error instanceof DiscordAPIError) {
			await interaction.editReply({ embeds: [noAccess] });
			return;
		}
		throw error;
	}

	await db.setBansSharingChannel(ctx.db, interaction.guild.id, channel.id);
	await interaction.editReply({
		embeds: [
			successEmbed(
				"Змінено канал сповіщень бота",
				`Новий канал сповіщень: ${channelMention(channel.id)}`,
			),
		],
	});
};

const checkConfig: CommandHandler = async (interaction, ctx) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.Administrator)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	await interaction.deferReply();

	const { guild } = interaction;
	const problems: [string, string][] = [];

	// Without this the gateway never delivers ban events, so sharing would only
	// ever work through the manual command.
	const me = await guild.members.fetchMe();
	if (!me.permissions.has(PermissionFlagsBits.ViewAuditLog)) {
		problems.push([
			"Відсутній дозвіл на перегляд Audit Log.",
			"Надайте боту доступ до Audit Log.",
		]);
	}

	const stored = await db.getGuild(ctx.db, guild.id);
	if (stored?.bans_sharing_channel_id) {
		const channelId = stored.bans_sharing_channel_id;
		try {
			const channel = await fetchSendableChannel(guild, channelId);
			if (!channel) {
				throw new Error("Channel is gone or is not a text channel.");
			}
			const posted = await channel.send({
				embeds: [
					{
						title: "Перевірка",
						description: "Тестове повідомлення-вставка (embed).",
					},
				],
			});
			await posted.reply({ content: "Тестове текстове повідомлення." });
		} catch (error) {
			problems.push([
				`Не вдалося відправити повідомлення в канал ${channelMention(channelId)}.`,
				// Embed field values cannot be empty, and an error body can be.
				userFacingMessage(error),
			]);
		}
	} else {
		problems.push([
			"Не налаштовано канал сповіщень.",
			"Налаштуйте канал сповіщень за допомогою команди `/bans_sharing set_channel`",
		]);
	}

	const trusted = await db.listTrustedModerators(ctx.db, guild.id);
	const names = trusted.map(
		(moderator) => `${moderator.user_global_name} (${moderator.user_id})`,
	);

	await interaction.editReply({
		embeds: [
			{
				title: "Результати перевірки налаштувань шарингу банів",
				description:
					problems.length === 0
						? `Все ок.\nДовірені модератори: ${names.length ? names.join(", ") : "немає"}`
						: "Помилка. Необхідні наступні права для каналу сповіщень:\n* View Channel\n* Send Messages\n* Read Messages History\n* Embed Links",
				color: problems.length === 0 ? Color.green : Color.red,
				fields: problems.map(([name, value]) => ({
					name,
					value,
					inline: false,
				})),
			},
		],
	});
};

const addTrustedModerator: CommandHandler = async (interaction, ctx) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.BanMembers)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	// A snowflake rather than a user option on purpose: the point of the feature
	// is trusting a moderator from another server, and a user picker only offers
	// members of this one.
	const userId = interaction.options.getString("user_id", true);
	// Checked before it reaches a bigint column, which would raise a cast error.
	const user = isSnowflake(userId)
		? await interaction.client.users.fetch(userId).catch(() => null)
		: null;
	if (!user) {
		await interaction.reply({ embeds: [notFound(userId)] });
		return;
	}

	const added = await db.addTrustedModerator(ctx.db, {
		guild_id: interaction.guild.id,
		user_id: user.id,
		user_global_name: user.displayName,
		created_by: interaction.user.id,
	});
	if (!added) {
		await interaction.reply({
			embeds: [
				errorEmbed(
					"Помилка",
					`Користувач ${user.displayName} вже є довіреним модератором на цьому сервері.`,
				),
			],
		});
		return;
	}
	await interaction.reply({
		embeds: [
			successEmbed(
				"Успішно",
				`Додано довіреного модератора: ${user.displayName}. За умови наявності відповідних дозволів у бота, бани цього модератора на інших серверах будуть автоматично застосовані і тут.`,
			),
		],
	});
};

const removeTrustedModerator: CommandHandler = async (interaction, ctx) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.BanMembers)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	const userId = interaction.options.getString("user_id", true);
	const removed = isSnowflake(userId)
		? await db.removeTrustedModerator(ctx.db, interaction.guild.id, userId)
		: null;
	if (!removed) {
		await interaction.reply({
			embeds: [
				errorEmbed(
					"Користувача не знайдено",
					`Користувач з ідентифікатором ${userId} не є довіреним модератором.`,
				),
			],
		});
		return;
	}
	await interaction.reply({
		embeds: [
			successEmbed(
				"Успішно",
				`Видалено модератора з довірених: ${removed.user_global_name}.`,
			),
		],
	});
};

export const bansSharing: CommandHandler = async (interaction, ctx) => {
	switch (interaction.options.getSubcommand()) {
		case "share":
			return share(interaction, ctx);
		case "set_channel":
			return setChannel(interaction, ctx);
		case "check_config":
			return checkConfig(interaction, ctx);
		case "add_trusted_moderator":
			return addTrustedModerator(interaction, ctx);
		case "remove_trusted_moderator":
			return removeTrustedModerator(interaction, ctx);
		default:
			await interaction.reply(ephemeralError("Помилка", "Невідома команда."));
	}
};

// Buttons on ban notices in receiving servers.

export const banButton: ButtonHandler = async (interaction) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.BanMembers)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	const embed = interaction.message.embeds[0]?.toJSON();
	const targetId = embed ? embedField(embed, TARGET_ID_FIELD) : undefined;
	if (!embed || !targetId) {
		await interaction.reply(
			ephemeralError("Помилка", "Повідомлення не містить даних бану."),
		);
		return;
	}
	const reason = embedReason(embed);

	// The ban is applied in the guild the button was clicked in, never the one
	// named in the embed: the embed is editable in principle, the interaction's
	// guild is signed by Discord.
	await interaction.deferUpdate();
	try {
		await interaction.guild.bans.create(targetId, {
			...(reason !== undefined && { reason }),
		});
	} catch (error) {
		if (error instanceof DiscordAPIError) {
			await interaction.editReply({
				embeds: [
					{
						...embed,
						description: `**Статус:** не вдалося забанити (Discord відповів ${error.status}). Перевірте права бота або скористайтеся текстовою командою нижче.`,
					},
				],
				components: banButtons(false),
			});
			return;
		}
		throw error;
	}

	await interaction.editReply({
		embeds: [
			{
				...embed,
				description: `**Статус:** теж забанено модератором ${userMention(interaction.user.id)}.`,
			},
		],
		components: banButtons(true),
	});
};

export const skipButton: ButtonHandler = async (interaction) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.BanMembers)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	const embed = interaction.message.embeds[0]?.toJSON() ?? {};
	await interaction.update({
		embeds: [
			{
				...embed,
				description: `**Статус:** проігноровано модератором ${userMention(interaction.user.id)}`,
			},
		],
		components: banButtons(true),
	});
};
