/**
 * Registers application commands with Discord. Run from the command line with
 * `npm run register`; it is not part of the Worker.
 *
 * Global registration can take up to an hour to propagate. Set
 * DISCORD_DEV_GUILD_ID to register into a single server instantly instead.
 */
/// <reference types="node" />
import { existsSync } from "node:fs";
import process from "node:process";

import { COMMANDS } from "./commands.ts";

if (existsSync(".dev.vars")) {
	process.loadEnvFile(".dev.vars");
}

const token = process.env.DISCORD_TOKEN;
const applicationId = process.env.DISCORD_APPLICATION_ID;
const guildId = process.env.DISCORD_DEV_GUILD_ID;

if (!token) {
	throw new Error("The DISCORD_TOKEN environment variable is required.");
}
if (!applicationId) {
	throw new Error(
		"The DISCORD_APPLICATION_ID environment variable is required.",
	);
}

const scope = guildId ? `guilds/${guildId}/commands` : "commands";
const url = `https://discord.com/api/v10/applications/${applicationId}/${scope}`;

const response = await fetch(url, {
	method: "PUT",
	headers: {
		"content-type": "application/json",
		authorization: `Bot ${token}`,
	},
	body: JSON.stringify(COMMANDS),
});

if (response.ok) {
	const registered = (await response.json()) as { name: string }[];
	console.log(
		`Registered ${registered.length} commands (${scope}): ${registered
			.map((command) => command.name)
			.join(", ")}`,
	);
} else {
	console.error(
		`Error registering commands: ${response.status} ${response.statusText}\n${await response.text()}`,
	);
	process.exitCode = 1;
}
