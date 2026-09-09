/**
 * The ban notice embed and the fan-out to participating servers.
 *
 * Everything a button needs is carried in the embed's fields, so no state is
 * kept between posting a notice and someone clicking it. That also means the
 * buttons keep working across a restart.
 */
import {
	type APIActionRowComponent,
	type APIComponentInMessageActionRow,
	type APIEmbed,
	ButtonStyle,
	type Client,
	ComponentType,
	MessageFlags,
	PermissionFlagsBits,
	type User,
	userMention,
} from "discord.js";

import * as db from "../../db.ts";
import { fetchSendableChannel } from "../../discord.ts";

export const BAN_BUTTON_ID = "bans_sharing:ban";
export const SKIP_BUTTON_ID = "bans_sharing:skip";

export const BANNED_FIELD = "Забанений";
export const GUILD_ID_FIELD = "guild_id";
export const ACTOR_ID_FIELD = "actor_id";
export const TARGET_ID_FIELD = "target_id";
export const REASON_FIELD = "reason";

/**
 * Embed field values cannot be empty, so an absent reason needs a stand-in.
 * The zero-width space renders as nothing and cannot be typed by a moderator,
 * so a literal reason never collides with it.
 */
export const NO_REASON = "​";

export interface Ban {
	guildId: string;
	guildName: string;
	actor: User;
	target: User;
	reason: string | undefined;
}

export function banEmbed(ban: Ban): APIEmbed {
	const embed: APIEmbed = {
		title: `Бан на сервері ${ban.guildName}`,
		fields: [
			{ name: "Сервер", value: ban.guildName },
			{
				name: "Модератор",
				value: `${ban.actor.displayName} '${ban.actor.username}'`,
			},
			{
				name: BANNED_FIELD,
				value: `${userMention(ban.target.id)} '${ban.target.displayName}' '${ban.target.username}'`,
			},
			{ name: GUILD_ID_FIELD, value: ban.guildId },
			{ name: ACTOR_ID_FIELD, value: ban.actor.id },
			{ name: TARGET_ID_FIELD, value: ban.target.id },
			{ name: REASON_FIELD, value: ban.reason || NO_REASON },
		],
	};
	const thumbnail = ban.target.avatarURL();
	if (thumbnail) {
		embed.thumbnail = { url: thumbnail };
	}
	return embed;
}

export function embedField(embed: APIEmbed, name: string): string | undefined {
	return embed.fields?.find((field) => field.name === name)?.value;
}

/** The reason as stored in an embed, mapping the stand-in back to nothing. */
export function embedReason(embed: APIEmbed): string | undefined {
	const value = embedField(embed, REASON_FIELD);
	return value === NO_REASON ? undefined : value;
}

export function banButtons(
	disabled: boolean,
): APIActionRowComponent<APIComponentInMessageActionRow>[] {
	return [
		{
			type: ComponentType.ActionRow,
			components: [
				{
					type: ComponentType.Button,
					style: ButtonStyle.Danger,
					label: "Теж забанити",
					custom_id: BAN_BUTTON_ID,
					disabled,
				},
				{
					type: ComponentType.Button,
					style: ButtonStyle.Secondary,
					label: "Ігнорувати",
					custom_id: SKIP_BUTTON_ID,
					disabled,
				},
			],
		},
	];
}

export function banCommandText(
	targetId: string,
	reason: string | undefined,
): string {
	// `delete_messages` is left empty on purpose: its values depend on the
	// moderator's interface language.
	return `/ban user:${targetId} delete_messages:${reason ? ` reason: ${reason}` : ""}`;
}

/**
 * Posts the ban to one participating server. Servers where the bot lacks Ban
 * Members get the copy-pasteable command instead of buttons that could only
 * fail.
 */
async function notifyGuild(
	client: Client,
	queryable: db.Queryable,
	ban: Ban,
	destination: db.BansSharingChannel,
): Promise<void> {
	const guild = await client.guilds.fetch(destination.guild_id);
	const channel = await fetchSendableChannel(guild, destination.channel_id);
	if (!channel) {
		throw new Error(
			`Channel ${destination.channel_id} in guild ${destination.guild_id} is gone or cannot be posted to.`,
		);
	}
	const me = await guild.members.fetchMe();
	const canBan = me.permissions.has(PermissionFlagsBits.BanMembers);

	const embed = banEmbed(ban);
	embed.title = "Новий бан на іншому сервері";
	const content = embedField(embed, BANNED_FIELD);

	let autoBanned = false;
	if (
		canBan &&
		(await db.isTrustedModerator(queryable, destination.guild_id, ban.actor.id))
	) {
		try {
			await guild.bans.create(ban.target.id, {
				...(ban.reason !== undefined && { reason: ban.reason }),
			});
			autoBanned = true;
		} catch (error) {
			// Fall through to the manual flow when the ban itself is refused.
			console.error(error);
		}
	}

	// Posting is deliberately outside the try above: a send that fails after the
	// ban went through must not fall through to the manual flow, which would
	// re-post the same embed with live buttons for a user already banned here.
	if (autoBanned) {
		embed.description = `**Статус:** застосовано автоматично, довірений модератор ${ban.actor.displayName} (${ban.actor.id})`;
		await channel.send({
			...(content && { content }),
			embeds: [embed],
			components: banButtons(true),
		});
		return;
	}

	embed.footer = {
		text: canBan
			? "Якщо кнопки з якоїсь причини не працюють, скористайтеся командою нижче."
			: "У бота відсутні права на бан. Для створення такого самого бану на цьому сервері вам доведеться скопіювати та відправити текстову команду нижче.",
	};
	const posted = await channel.send({
		...(content && { content }),
		embeds: [embed],
		// Buttons the bot could not act on would only ever fail.
		...(canBan ? { components: banButtons(false) } : {}),
	});
	// The notice is what matters, and it is already posted. Failing to attach
	// the copy-pasteable command - Read Message History is missing, say - must
	// not make this server count as unreached.
	try {
		await posted.reply({
			content: banCommandText(ban.target.id, ban.reason),
			flags: MessageFlags.SuppressEmbeds,
		});
	} catch (error) {
		console.error(error);
	}
}

export interface FanOutResult {
	delivered: number;
	total: number;
}

/** Sends the ban to every participating server except the one it came from. */
export async function fanOut(
	client: Client,
	queryable: db.Queryable,
	ban: Ban,
): Promise<FanOutResult> {
	const destinations = await db.listBansSharingChannels(queryable, ban.guildId);
	let delivered = 0;
	for (const destination of destinations) {
		try {
			await notifyGuild(client, queryable, ban, destination);
			delivered += 1;
		} catch (error) {
			console.error(error);
		}
	}
	return { delivered, total: destinations.length };
}
