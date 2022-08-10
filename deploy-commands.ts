import { REST } from '@discordjs/rest';
import { Routes } from 'discord-api-types/v10';
import { commands } from './commands';
import {
  DISCORD_APPLICATION_ID,
  DISCORD_BOT_TOKEN,
  DISCORD_GUILD_IDS,
} from './config';

const rest = new REST({ version: '10' }).setToken(DISCORD_BOT_TOKEN);

DISCORD_GUILD_IDS.forEach((guild_id, guild_name) => {
  rest
    .put(Routes.applicationGuildCommands(DISCORD_APPLICATION_ID, guild_id), {
      body: commands.map((cmd) => cmd.command.toJSON()),
    })
    .then(() =>
      console.log(
        `${guild_name}: successfully registered application commands.`,
      ),
    )
    .catch(console.error);
});
