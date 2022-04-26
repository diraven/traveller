import { SlashCommandBuilder } from '@discordjs/builders';
import { itemsArrayToPages } from '../pager';

import * as paginationEmbed from 'discordjs-button-pagination';

import {
  Collection,
  CommandInteraction,
  GuildMemberRoleManager,
  Interaction,
  MessageButton,
  Role,
  MessageEmbed,
  Client,
} from 'discord.js';
import { APIRole } from 'discord-api-types/v10';

// enum EmbedColor {
//   Primary = "#007bff",
//   Info = "#17a2b8",
//   Success = "#28a745",
//   Warning = "#ffc107",
//   Danger = "#dc3545",
// }

function filterPublicRoles(
  interaction: Interaction,
  roles: Collection<string, Role>,
): Collection<string, Role> {
  return roles.filter((role) => roleIsPublic(interaction, role));
}

function roleIsPublic(interaction: Interaction, role: Role | APIRole): boolean {
  const bot_role = interaction.guild.members.resolve(interaction.applicationId)
    .roles.botRole;

  return (
    bot_role.position > role.position &&
    role !== interaction.guild.roles.everyone
  );
}

function getRolesNames(roles: Collection<string, Role>): Array<string> {
  return roles.map((role) => role.name);
}

export const builder = new SlashCommandBuilder()
  .setName('roles')
  .setDescription('Публічні ролі')
  // List.
  .addSubcommand((subcommand) =>
    subcommand.setName('list').setDescription('Список публічних ролей'),
  )

  // My.
  .addSubcommand((subcommand) =>
    subcommand.setName('my').setDescription('Мої публічні ролі'),
  )

  // Who.
  .addSubcommand((subcommand) =>
    subcommand
      .setName('who')
      .setDescription('Хто має публічну роль')
      .addRoleOption((option) =>
        option.setName('role').setDescription('Оберіть роль').setRequired(true),
      ),
  )

  // Join.
  .addSubcommand((subcommand) =>
    subcommand
      .setName('join')
      .setDescription('Долучитися')
      .addRoleOption((option) =>
        option.setName('role').setDescription('Оберіть роль').setRequired(true),
      ),
  )

  // Leave.
  .addSubcommand((subcommand) =>
    subcommand
      .setName('leave')
      .setDescription('Покинути роль')
      .addRoleOption((option) =>
        option.setName('role').setDescription('Оберіть роль').setRequired(true),
      ),
  );

async function sendPages(
  interaction: CommandInteraction,
  items: Array<string>,
  title: string,
  titleEmpty: string = 'Немає даних',
) {
  const paginationButtons = [
    new MessageButton()
      .setCustomId('previousbtn')
      .setLabel('<')
      .setStyle('PRIMARY'),
    new MessageButton()
      .setCustomId('nextbtn')
      .setLabel('>')
      .setStyle('PRIMARY'),
  ];
  const paginationTimeout = 60000;

  const pages = itemsArrayToPages(items, title);

  if (pages.length > 0) {
    paginationEmbed(interaction, pages, paginationButtons, paginationTimeout);
  } else {
    await interaction.reply({
      embeds: [new MessageEmbed().setTitle(titleEmpty)],
    });
  }
}

export function init(client: Client) {
  client.on('interactionCreate', async (interaction) => {
    // Command.
    if (interaction.isCommand()) {
      // List.
      if (interaction.options.getSubcommand() === 'list') {
        sendPages(
          interaction,
          getRolesNames(
            filterPublicRoles(
              interaction,
              await interaction.guild.roles.fetch(),
            ),
          ).sort(),
          'Публічні ролі',
          'Нема публічних ролей',
        );
      }

      // My.
      if (interaction.options.getSubcommand() === 'my') {
        sendPages(
          interaction,
          getRolesNames(
            filterPublicRoles(
              interaction,
              (interaction.member.roles as GuildMemberRoleManager).cache,
            ),
          ).sort(),
          'Твої публічні ролі',
          'Не маєш публічних ролей',
        );
      }

      // Who.
      if (interaction.options.getSubcommand() === 'who') {
        const role = interaction.options.getRole('role');
        if (roleIsPublic(interaction, role)) {
          const members = (interaction.options.getRole('role') as Role).members;
          console.log(members);
          sendPages(
            interaction,
            members.map(
              (member) =>
                `${member.user.username}#${member.user.discriminator}`,
            ),
            `Хто долучився до ${role.name}`,
            `Ніхто не долучився до ${role.name}`,
          );
        }
      }

      // Join.
      if (interaction.options.getSubcommand() === 'join') {
        const role = interaction.options.getRole('role') as Role;
        if (roleIsPublic(interaction, role)) {
          (interaction.member.roles as GuildMemberRoleManager).add(role).then(
            async () =>
              await interaction.reply({
                embeds: [
                  new MessageEmbed().setTitle(`Тепер маєш роль ${role.name}.`),
                ],
              }),
          );
        } else {
          await interaction.reply({
            embeds: [
              new MessageEmbed().setTitle(
                `Дія неможлива: роль ${role.name} не є публічною.`,
              ),
            ],
          });
        }
      }

      // Leave.
      if (interaction.options.getSubcommand() === 'leave') {
        const role = interaction.options.getRole('role') as Role;
        if (roleIsPublic(interaction, role)) {
          (interaction.member.roles as GuildMemberRoleManager)
            .remove(role)
            .then(
              async () =>
                await interaction.reply({
                  embeds: [
                    new MessageEmbed().setTitle(
                      `Більше не маєш ролі ${role.name}.`,
                    ),
                  ],
                }),
            );
        } else {
          await interaction.reply({
            embeds: [
              new MessageEmbed().setTitle(
                `Дія неможлива: роль ${role.name} не є публічною.`,
              ),
            ],
          });
        }
      }
    }
  });
}
