/**
 * The origin side of ban sharing: the bot watches the audit log, and when a
 * moderator bans someone it asks in that server's notification channel whether
 * to pass the ban on. Nothing leaves the server until someone confirms.
 */
import {
	type APIActionRowComponent,
	type APIComponentInMessageActionRow,
	type APIEmbed,
	AuditLogEvent,
	ButtonStyle,
	type Client,
	ComponentType,
	type Guild,
	type GuildAuditLogsEntry,
	type Message,
	MessageFlags,
	PermissionFlagsBits,
	userMention,
} from "discord.js";

import type { ButtonHandler } from "../../context.ts";
import * as db from "../../db.ts";
import {
	ephemeralError,
	fetchSendableChannel,
	NO_ACCESS,
} from "../../discord.ts";
import {
	ACTOR_ID_FIELD,
	BANNED_FIELD,
	type Ban,
	banCommandText,
	banEmbed,
	embedField,
	embedReason,
	fanOut,
	TARGET_ID_FIELD,
} from "./share.ts";

export const SHARE_BUTTON_ID = "bans_sharing:share";
export const NO_SHARE_BUTTON_ID = "bans_sharing:no_share";

/** How long the prompt stays actionable before it marks itself ignored. */
const PROMPT_TIMEOUT_MS = 24 * 60 * 60 * 1000;

const NO_BAN_DATA = ephemeralError(
	"Помилка",
	"Повідомлення не містить даних бану.",
);

function confirmButtons(
	disabled: boolean,
): APIActionRowComponent<APIComponentInMessageActionRow>[] {
	return [
		{
			type: ComponentType.ActionRow,
			components: [
				{
					type: ComponentType.Button,
					style: ButtonStyle.Danger,
					label: "Поширити на інші сервери",
					custom_id: SHARE_BUTTON_ID,
					disabled,
				},
				{
					type: ComponentType.Button,
					style: ButtonStyle.Secondary,
					label: "Не поширювати",
					custom_id: NO_SHARE_BUTTON_ID,
					disabled,
				},
			],
		},
	];
}

/**
 * Asks the origin server whether to share a ban it just saw in its audit log.
 *
 * The ban is marked seen as soon as the prompt goes up, matching the gateway
 * bot: one prompt per banned user across the whole network. When the server has
 * no notification channel nothing is recorded, so another server banning the
 * same user still gets its own prompt.
 */
export async function promptToShare(
	client: Client,
	queryable: db.Queryable,
	ban: Ban,
): Promise<void> {
	// Read the configuration before claiming: a server with no notification
	// channel must leave the ban unclaimed, so another server banning the same
	// user still gets its own prompt.
	const stored = await db.getGuild(queryable, ban.guildId);
	if (!stored?.bans_sharing_channel_id) {
		return;
	}

	const guild = await client.guilds.fetch(ban.guildId);
	const channel = await fetchSendableChannel(
		guild,
		stored.bans_sharing_channel_id,
	);
	if (!channel) {
		throw new Error(
			`Channel ${stored.bans_sharing_channel_id} in guild ${ban.guildId} is gone or cannot be posted to.`,
		);
	}

	// The claim is the deduplication: whoever inserts the row owns this ban.
	if (
		!(await db.claimBan(queryable, ban.target.id, ban.actor.id, ban.reason))
	) {
		return;
	}

	const embed = banEmbed(ban);
	embed.title = "Новий бан на цьому сервері";
	embed.footer = {
		text: "Для застосування бану вручну, скористайтеся командою нижче.",
	};
	const content = embedField(embed, BANNED_FIELD);

	let posted: Message;
	try {
		posted = await channel.send({
			...(content && { content }),
			embeds: [embed],
			components: confirmButtons(false),
		});
	} catch (error) {
		// Nobody was told, so the ban has to stay shareable - otherwise it is
		// marked seen network-wide and silently disappears. Missing Send Messages
		// or Embed Links on the notification channel lands here.
		await db.releaseBan(queryable, ban.target.id);
		throw error;
	}

	// The prompt is up, so the claim stands even if the follow-up fails: losing
	// the copy-pasteable command is a cosmetic problem, losing the ban is not.
	try {
		await posted.reply({
			content: banCommandText(ban.target.id, ban.reason),
			flags: MessageFlags.SuppressEmbeds,
		});
	} catch (error) {
		console.error(error);
	}

	// Matches the gateway bot's 24 hour view timeout. A restart drops the timer,
	// which leaves the buttons live rather than breaking them - they carry all
	// their state in the embed.
	setTimeout(() => {
		void expirePrompt(posted.id, channel.id, client);
	}, PROMPT_TIMEOUT_MS).unref();
}

async function expirePrompt(
	messageId: string,
	channelId: string,
	client: Client,
): Promise<void> {
	try {
		const channel = await client.channels.fetch(channelId);
		if (!channel?.isTextBased()) {
			return;
		}
		const message = await channel.messages.fetch(messageId);
		const embed = message.embeds[0]?.toJSON();
		// A description means a moderator already decided.
		if (!embed || embed.description) {
			return;
		}
		await message.edit({
			embeds: [{ ...embed, description: "**Статус:** проігноровано" }],
			components: confirmButtons(true),
		});
	} catch (error) {
		console.error(error);
	}
}

/** Rebuilds the ban an embed describes, so buttons need no stored state. */
async function banFromEmbed(
	client: Client,
	guild: Guild,
	embed: APIEmbed,
): Promise<Ban | null> {
	const actorId = embedField(embed, ACTOR_ID_FIELD);
	const targetId = embedField(embed, TARGET_ID_FIELD);
	if (!actorId || !targetId) {
		return null;
	}
	// Either account may have been deleted since the notice went up, and by now
	// the interaction is already acknowledged: report it as a status rather than
	// throwing and leaving the notice stuck mid-share.
	try {
		return {
			guildId: guild.id,
			guildName: guild.name,
			actor: await client.users.fetch(actorId),
			target: await client.users.fetch(targetId),
			reason: embedReason(embed),
		};
	} catch (error) {
		console.error(error);
		return null;
	}
}

/**
 * A status line in the description means the prompt has already been answered,
 * by another moderator or by the expiry timer. Discord leaves stale buttons
 * clickable, so both handlers check before acting.
 */
const ALREADY_ANSWERED = ephemeralError("Помилка", "Цей бан вже опрацьовано.");

export const shareButton: ButtonHandler = async (interaction, ctx) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.BanMembers)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	const embed = interaction.message.embeds[0]?.toJSON();
	if (!embed) {
		await interaction.reply(NO_BAN_DATA);
		return;
	}
	if (embed.description) {
		await interaction.reply(ALREADY_ANSWERED);
		return;
	}

	// Acknowledged first, and with the buttons disabled: resolving the users
	// below needs REST calls that can outlast the three-second deadline, and a
	// live button in the meantime would let a second moderator share twice.
	const actor = interaction.user;
	await interaction.update({
		embeds: [
			{
				...embed,
				description: `**Статус:** поширюється модератором ${userMention(actor.id)}`,
			},
		],
		components: confirmButtons(true),
	});

	// The fan-out is attributed to the guild the button was clicked in, never
	// the one named in the embed: embeds are editable in principle, the
	// interaction's guild is signed by Discord.
	const ban = await banFromEmbed(interaction.client, interaction.guild, embed);
	if (!ban) {
		await interaction.editReply({
			embeds: [
				{
					...embed,
					description: "**Статус:** не вдалося поширити, дані бану неповні.",
				},
			],
			components: confirmButtons(true),
		});
		return;
	}

	let delivered: number;
	let total: number;
	try {
		({ delivered, total } = await fanOut(interaction.client, ctx.db, ban));
	} catch (error) {
		// fanOut swallows per-server failures, so a throw comes from reading the
		// destination list - before anything was sent anywhere. Say so on the
		// prompt first, since that cannot fail for the same reason, then release
		// the claim so `/bans_sharing share` can retry. Without either the prompt
		// stays "поширюється" forever with nobody notified.
		await interaction.editReply({
			embeds: [
				{
					...embed,
					description:
						"**Статус:** не вдалося поширити. Спробуйте `/bans_sharing share`.",
				},
			],
			components: confirmButtons(true),
		});
		await db.releaseBan(ctx.db, ban.target.id);
		throw error;
	}

	await interaction.editReply({
		embeds: [
			{
				...embed,
				description: `**Статус:** поширено на ${delivered} з ${total} серверів модератором ${userMention(actor.id)}`,
			},
		],
		components: confirmButtons(true),
	});
};

export const noShareButton: ButtonHandler = async (interaction) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.BanMembers)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	const embed = interaction.message.embeds[0]?.toJSON() ?? {};
	if (embed.description) {
		await interaction.reply(ALREADY_ANSWERED);
		return;
	}
	await interaction.update({
		embeds: [
			{
				...embed,
				description: `**Статус:** проігноровано модератором ${userMention(interaction.user.id)}`,
			},
		],
		components: confirmButtons(true),
	});
};

/**
 * The audit log listener. Requires the View Audit Log permission and the
 * GuildModeration intent; without them Discord simply never sends the event.
 */
export function onAuditLogEntry(client: Client, queryable: db.Queryable) {
	return async (entry: GuildAuditLogsEntry, guild: Guild): Promise<void> => {
		if (entry.action !== AuditLogEvent.MemberBanAdd) {
			return;
		}
		if (!entry.executorId || !entry.targetId) {
			return;
		}
		// Bans the bot itself applied are echoes of a share, not new bans.
		if (entry.executorId === client.user?.id) {
			return;
		}

		const [actor, target] = await Promise.all([
			client.users.fetch(entry.executorId),
			client.users.fetch(entry.targetId),
		]);
		await promptToShare(client, queryable, {
			guildId: guild.id,
			guildName: guild.name,
			actor,
			target,
			reason: entry.reason ?? undefined,
		});
	};
}
