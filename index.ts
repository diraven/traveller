// @ts-check

import { Client, GatewayIntentBits } from 'discord.js';
import { DISCORD_BOT_TOKEN } from './config';
import { commands } from './commands';

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildPresences,
  ],
});

client.once('ready', () => {
  console.log('Ready!');
});

commands.forEach((command) => command.init(client));

client.login(DISCORD_BOT_TOKEN);
