import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { Command } from "../types/command";

export const cmd: Command = {
  data: new SlashCommandBuilder()
    .setName("user")
    .setDescription("Replies with User Data!"),
  execute: async function execute(interaction: CommandInteraction) {
    await interaction.reply(
      `Your tag: ${interaction.user.tag}
Your id: ${interaction.user.id}`
    );
  },
};
