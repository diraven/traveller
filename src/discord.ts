/**
 * Small presentation helpers shared by the handlers. discord.js covers the
 * REST, gateway and permission work, so what is left here is the embed
 * vocabulary the bot has always used.
 */
import {
	type APIEmbed,
	DiscordAPIError,
	HTTPError,
	type InteractionReplyOptions,
	MessageFlags,
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

export function truncate(text: string, maxLength: number): string {
	return text.length < maxLength ? text : `${text.slice(0, maxLength)}...`;
}
