import { roleMention, SlashCommandBuilder } from "@discordjs/builders";
import { itemsArrayToPages } from "../pager";
import { v4 as uuidv4 } from "uuid";

import * as paginationEmbed from "discordjs-button-pagination";

import {
  Collection,
  CommandInteraction,
  Guild,
  GuildMemberRoleManager,
  Interaction,
  MessageActionRow,
  MessageButton,
  MessageSelectMenu,
  Options,
  Role,
  RoleManager,
  MessageEmbed,
  Client,
} from "discord.js";
import { Command } from "../types/command";
import { idText } from "typescript";
import { APIRole } from "discord-api-types/v10";

enum EmbedColor {
  Primary = "#007bff",
  Info = "#17a2b8",
  Success = "#28a745",
  Warning = "#ffc107",
  Danger = "#dc3545",
}

function filterPublicRoles(
  interaction: Interaction,
  roles: Collection<string, Role>
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

export let builder = new SlashCommandBuilder()
  .setName("roles")
  .setDescription("Публічні ролі")
  // List.
  .addSubcommand((subcommand) =>
    subcommand.setName("list").setDescription("Список публічних ролей")
  )

  // My.
  .addSubcommand((subcommand) =>
    subcommand.setName("my").setDescription("Мої публічні ролі")
  )

  // Who.
  .addSubcommand((subcommand) =>
    subcommand
      .setName("who")
      .setDescription("Хто має")
      .addRoleOption((option) =>
        option.setName("role").setDescription("Оберіть роль").setRequired(true)
      )
  )

  // Join.
  .addSubcommand((subcommand) =>
    subcommand
      .setName("join")
      .setDescription("Долучитися")
      .addRoleOption((option) =>
        option.setName("role").setDescription("Оберіть роль").setRequired(true)
      )
  )

  // Leave.
  .addSubcommand((subcommand) =>
    subcommand
      .setName("leave")
      .setDescription("Покинути роль")
      .addRoleOption((option) =>
        option.setName("role").setDescription("Оберіть роль").setRequired(true)
      )
  );

async function sendPages(interaction, items: Array<string>, title: string) {
  const paginationButtons = [
    new MessageButton()
      .setCustomId("previousbtn")
      .setLabel("<")
      .setStyle("PRIMARY"),
    new MessageButton()
      .setCustomId("nextbtn")
      .setLabel(">")
      .setStyle("PRIMARY"),
  ];
  const paginationTimeout = 60000;

  let pages = itemsArrayToPages(items, title);

  if (pages.length > 0) {
    paginationEmbed(interaction, pages, paginationButtons, paginationTimeout);
  } else {
    console.log("no pages");
    // TODO:
  }
}

export function init(client: Client) {
  client.on("interactionCreate", async (interaction) => {
    // Command.
    if (interaction.isCommand()) {
      // List.
      if (interaction.options.getSubcommand() === "list") {
        sendPages(
          interaction,
          getRolesNames(
            filterPublicRoles(
              interaction,
              await interaction.guild.roles.fetch()
            )
          ).sort(),
          "Публічні ролі"
        );
      }

      // My.
      if (interaction.options.getSubcommand() === "my") {
        sendPages(
          interaction,
          getRolesNames(
            filterPublicRoles(
              interaction,
              (interaction.member.roles as GuildMemberRoleManager).cache
            )
          ).sort(),
          "Твої публічні ролі"
        );
      }

      // Who.
      if (interaction.options.getSubcommand() === "who") {
        let role = interaction.options.getRole("role");
        if (roleIsPublic(interaction, role)) {
          let members = (interaction.options.getRole("role") as Role).members;
          console.log(members);
          sendPages(
            interaction,
            members.map(
              (member) => `${member.user.username}#${member.user.discriminator}`
            ),
            `Хто долучився до ${role.name}`
          );
        }
      }

      // Join.
      if (interaction.options.getSubcommand() === "join") {
        let role = interaction.options.getRole("role") as Role;
        if (roleIsPublic(interaction, role)) {
          // TODO: add role.
        } else {
          // TODO: raise error.
        }
      }

      // Leave.
      if (interaction.options.getSubcommand() === "leave") {
        let role = interaction.options.getRole("role") as Role;
        if (roleIsPublic(interaction, role)) {
          // TODO: remove role.
        } else {
          // TODO: raise error.
        }
      }
    }
  });
}
