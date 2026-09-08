/**
 * What every handler is given: the interaction discord.js parsed, plus the
 * database. Handlers reply for themselves; `src/index.ts` catches whatever
 * they throw and turns it into an error embed.
 *
 * The `"cached"` type parameter says the interaction came from a guild the bot
 * is in, so `interaction.guild` and `interaction.member` are never null. The
 * dispatcher checks that before calling a handler.
 */
import type {
	ButtonInteraction,
	ChatInputCommandInteraction,
	UserContextMenuCommandInteraction,
} from "discord.js";

import type { Queryable } from "./db.ts";

export interface Context {
	db: Queryable;
}

export type CommandHandler = (
	interaction: ChatInputCommandInteraction<"cached">,
	ctx: Context,
) => Promise<void>;

export type UserCommandHandler = (
	interaction: UserContextMenuCommandInteraction<"cached">,
	ctx: Context,
) => Promise<void>;

export type ButtonHandler = (
	interaction: ButtonInteraction<"cached">,
	ctx: Context,
) => Promise<void>;
