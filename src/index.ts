/**
 * The bot process: connects to the Discord gateway, applies pending database
 * migrations, and routes interactions and audit log events to handlers.
 */
import "./sentry.ts";

import process from "node:process";
import {
	Client,
	Events,
	GatewayIntentBits,
	type Interaction,
	MessageFlags,
} from "discord.js";
import pg from "pg";

import {
	BANS_SHARING_COMMAND,
	COMMANDS,
	FAQ_COMMAND,
	RUSNI_PYZDA_COMMAND,
	SHARE_BAN_USER_COMMAND,
	SLAP_COMMAND,
	VERIFICATION_COMMAND,
	VERIFY_COMMAND,
} from "./commands.ts";
import { config } from "./config.ts";
import type {
	ButtonHandler,
	CommandHandler,
	Context,
	UserCommandHandler,
} from "./context.ts";
import * as db from "./db.ts";
import { errorEmbed, userFacingMessage } from "./discord.ts";
import { reconcileGuilds } from "./guilds.ts";
import {
	BAN_BUTTON_ID,
	banButton,
	bansSharing,
	NO_SHARE_BUTTON_ID,
	noShareButton,
	onAuditLogEntry,
	SHARE_BUTTON_ID,
	SKIP_BUTTON_ID,
	shareBanUserCommand,
	shareButton,
	skipButton,
} from "./handlers/bans_sharing/index.ts";
import { faq } from "./handlers/faq.ts";
import { rusniPyzda } from "./handlers/rusni_pyzda.ts";
import { slap } from "./handlers/slap.ts";
import { verification, verify } from "./handlers/verification.ts";
import { migrate } from "./migrate.ts";
import { captureError } from "./sentry.ts";

const CHAT_INPUT_HANDLERS: Record<string, CommandHandler> = {
	[FAQ_COMMAND.name]: faq,
	[SLAP_COMMAND.name]: slap,
	[RUSNI_PYZDA_COMMAND.name]: rusniPyzda,
	[VERIFICATION_COMMAND.name]: verification,
	[VERIFY_COMMAND.name]: verify,
	[BANS_SHARING_COMMAND.name]: bansSharing,
};

const USER_COMMAND_HANDLERS: Record<string, UserCommandHandler> = {
	[SHARE_BAN_USER_COMMAND.name]: shareBanUserCommand,
};

const BUTTON_HANDLERS: Record<string, ButtonHandler> = {
	[BAN_BUTTON_ID]: banButton,
	[SKIP_BUTTON_ID]: skipButton,
	[SHARE_BUTTON_ID]: shareButton,
	[NO_SHARE_BUTTON_ID]: noShareButton,
};

const pool = new pg.Pool({ connectionString: config.databaseUrl });
const ctx: Context = { db: pool };

const client = new Client({
	// GuildModeration is what makes Discord send audit log entries, which is how
	// bans are noticed in the first place.
	intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildModeration],
});

async function dispatch(interaction: Interaction): Promise<void> {
	if (!interaction.inCachedGuild()) {
		return;
	}
	if (interaction.isChatInputCommand()) {
		await CHAT_INPUT_HANDLERS[interaction.commandName]?.(interaction, ctx);
		return;
	}
	if (interaction.isUserContextMenuCommand()) {
		await USER_COMMAND_HANDLERS[interaction.commandName]?.(interaction, ctx);
		return;
	}
	if (interaction.isButton()) {
		await BUTTON_HANDLERS[interaction.customId]?.(interaction, ctx);
	}
}

/** Tells the user something went wrong, whatever state the reply is in. */
async function reportToUser(
	interaction: Interaction,
	error: unknown,
): Promise<void> {
	if (!interaction.isRepliable()) {
		return;
	}
	const payload = {
		embeds: [errorEmbed("Помилка", userFacingMessage(error))],
	};
	try {
		if (interaction.deferred || interaction.replied) {
			await interaction.followUp({
				...payload,
				flags: MessageFlags.Ephemeral,
			});
		} else {
			await interaction.reply({ ...payload, flags: MessageFlags.Ephemeral });
		}
	} catch (replyError) {
		captureError(replyError);
	}
}

client.on(Events.InteractionCreate, async (interaction) => {
	try {
		await dispatch(interaction);
	} catch (error) {
		captureError(error);
		await reportToUser(interaction, error);
	}
});

client.on(Events.GuildAuditLogEntryCreate, (entry, guild) => {
	onAuditLogEntry(client, ctx.db)(entry, guild).catch(captureError);
});

client.on(Events.GuildCreate, (guild) => {
	db.upsertGuild(ctx.db, guild.id, guild.name).catch(captureError);
});

client.on(Events.GuildDelete, (guild) => {
	db.deleteGuild(ctx.db, guild.id).catch(captureError);
});

client.on(Events.Error, captureError);
client.on(Events.ShardError, captureError);

client.once(Events.ClientReady, (ready) => {
	console.log(
		`Logged in as ${ready.user.tag}, ${ready.guilds.cache.size} guilds.`,
	);
	void (async () => {
		try {
			await reconcileGuilds(ready, ctx.db);
			const commands = config.devGuildId
				? await ready.application.commands.set(COMMANDS, config.devGuildId)
				: await ready.application.commands.set(COMMANDS);
			console.log(`Registered ${commands.size} commands.`);
		} catch (error) {
			captureError(error);
		}
	})();
});

process.on("unhandledRejection", captureError);
process.on("uncaughtException", captureError);

async function shutdown(signal: string): Promise<void> {
	console.log(`Received ${signal}, shutting down.`);
	await client.destroy();
	await pool.end();
	process.exit(0);
}

process.on("SIGTERM", () => void shutdown("SIGTERM"));
process.on("SIGINT", () => void shutdown("SIGINT"));

const applied = await migrate(pool);
if (applied.length) {
	console.log(`Applied migrations: ${applied.join(", ")}`);
}
await client.login(config.discordToken);
