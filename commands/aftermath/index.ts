import { SlashCommandBuilder } from '@discordjs/builders';

import { MessageEmbed, Client } from 'discord.js';

// enum EmbedColor {
//   Primary = "#007bff",
//   Info = "#17a2b8",
//   Success = "#28a745",
//   Warning = "#ffc107",
//   Danger = "#dc3545",
// }

export const builder = new SlashCommandBuilder()
  .setName('af')
  .setDescription('Aftermath - Вислід')
  .addSubcommand((subcommand) =>
    subcommand.setName('attack').setDescription('Атакувати.'),
  )
  .addSubcommand((subcommand) =>
    subcommand.setName('status').setDescription('Поточний стан речей.'),
  );

export function init(client: Client) {
  client.on('interactionCreate', async (interaction) => {
    // Command.
    if (interaction.isCommand() && interaction.commandName === builder.name) {
      if (interaction.options.getSubcommand() === 'attack') {
        await interaction.reply({
          embeds: [
            new MessageEmbed().setTitle('Атака:').setDescription(
              `
              test
              `,
            ),
          ],
        });
      }

      if (interaction.options.getSubcommand() === 'status') {
        await interaction.reply({
          embeds: [
            new MessageEmbed().setTitle('Поточний стан речей:').setDescription(
              `
              test
              `,
            ),
          ],
        });
      }
    }
  });
}
