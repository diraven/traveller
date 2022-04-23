import { REST } from "@discordjs/rest";
import { Routes } from "discord-api-types/v10";
import { commands } from "./commands";
import {
  DISCORD_APPLICATION_ID,
  DISCORD_BOT_GUILD_ID,
  DISCORD_BOT_TOKEN,
} from "./config";

const rest = new REST({ version: "10" }).setToken(DISCORD_BOT_TOKEN);

rest
  .put(
    Routes.applicationGuildCommands(
      DISCORD_APPLICATION_ID,
      DISCORD_BOT_GUILD_ID
    ),
    { body: commands.map((cmd) => cmd.data.toJSON()) }
  )
  .then(() => console.log("Successfully registered application commands."))
  .catch(console.error);
