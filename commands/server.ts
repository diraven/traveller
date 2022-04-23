import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { Command } from "../types/command";

export const cmd: Command = {
  data: new SlashCommandBuilder()
    .setName("server")
    .setDescription("Replies with Pong!"),
  execute: async function execute(interaction: CommandInteraction) {
    await interaction.reply(
      `Server name: ${interaction.guild.name}
Total members: ${interaction.guild.memberCount}`
    );
  },
};
