/**
 * Small presentation helpers shared by the handlers. discord.js covers the
 * REST, gateway and permission work, so what is left here is the embed
 * vocabulary the bot has always used.
 */
import {
	type APIEmbed,
	DiscordAPIError,
	type Guild,
	HTTPError,
	type InteractionReplyOptions,
	MessageFlags,
	type SendableChannels,
} from "discord.js";

/** Embed colors matching discord.py's `discord.Color` presets. */
export const Color = {
	red: 0xe74c3c,
	green: 0x2ecc71,
	blue: 0x3498db,
} as const;

export function errorEmbed(title: string, description: string): APIEmbed {
	return { title, description, color: Color.red };
}

export function successEmbed(title: string, description: string): APIEmbed {
	return { title, description, color: Color.green };
}

export function ephemeralError(
	title: string,
	description: string,
): InteractionReplyOptions {
	return {
		embeds: [errorEmbed(title, description)],
		flags: MessageFlags.Ephemeral,
	};
}

export const NO_ACCESS = ephemeralError("Помилка", "Відсутній доступ.");

/** Keeps internal detail such as request paths out of public channels. */
export function userFacingMessage(error: unknown): string {
	if (error instanceof DiscordAPIError || error instanceof HTTPError) {
		return `Discord відповів помилкою ${error.status}.`;
	}
	return "Спробуйте ще раз пізніше.";
}

/** The largest value a signed bigint column holds. */
const MAX_BIGINT = 9223372036854775807n;

/**
 * Discord snowflakes are numeric. Commands that take one as text have to check
 * before it reaches a bigint column, which would otherwise raise a cast error -
 * and the column is signed, so a longer number is out of range rather than
 * merely unknown. Real snowflakes stay well inside that for centuries: the top
 * bits are a millisecond timestamp.
 */
export function isSnowflake(value: string): boolean {
	return /^\d{17,19}$/.test(value) && BigInt(value) <= MAX_BIGINT;
}

/**
 * The channel if it exists and can be posted to, otherwise null.
 *
 * Two traps here. `channels.fetch(id)` throws rather than returning null when
 * the channel is gone, and `isSendable()` only checks the channel *type* - it
 * says nothing about permissions, so a send can still fail and callers have to
 * handle that separately.
 */
export async function fetchSendableChannel(
	guild: Guild,
	channelId: string,
): Promise<SendableChannels | null> {
	try {
		const channel = await guild.channels.fetch(channelId);
		return channel?.isSendable() ? channel : null;
	} catch (error) {
		if (error instanceof DiscordAPIError) {
			return null;
		}
		throw error;
	}
}
