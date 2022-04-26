// @ts-check

import { Client, Intents } from "discord.js";
import { DISCORD_BOT_TOKEN } from "./config";
import { commands } from "./commands";

const client = new Client({
  intents: [
    Intents.FLAGS.GUILDS,
    Intents.FLAGS.GUILD_MEMBERS,
    Intents.FLAGS.GUILD_PRESENCES,
  ],
});

client.once("ready", () => {
  console.log("Ready!");
});

commands.forEach((command) => command.init(client));

client.login(DISCORD_BOT_TOKEN);
