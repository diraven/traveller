import { roleMention, SlashCommandBuilder } from "@discordjs/builders";
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
} from "discord.js";
import { Command } from "../types/command";

async function getPublicRoles(guild: Guild) {
  return await guild.roles.fetch();
}

function filterPublicRoles(
  interaction: Interaction,
  roles: Collection<string, Role>
): Collection<string, Role> {
  return roles.filter((role) => roleIsPublic(interaction, role));
}

function roleIsPublic(interaction: Interaction, role: Role): boolean {
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

export const cmd: Command = {
  data: new SlashCommandBuilder()
    .setName("games")
    .setDescription("In development!")
    .addSubcommand((subcommand) =>
      subcommand.setName("list").setDescription("Список ігор")
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("my").setDescription("Мої ігри")
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("play")
        .setDescription("Хто грає")
        .addRoleOption((option) =>
          option
            .setName("role")
            .setDescription("Select a role")
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("додати")
        .setDescription("Додати гру")
        .addRoleOption((option) =>
          option
            .setName("role")
            .setDescription("Select a role")
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("прибрати")
        .setDescription("Прибрати гру")
        .addRoleOption((option) =>
          option
            .setName("role")
            .setDescription("Select a role")
            .setRequired(true)
        )
    ),

  execute: async function execute(interaction: CommandInteraction) {
    // const row = new MessageActionRow();

    // interaction.guild;

    // All Games.
    // if (interaction.options.getSubcommand() === "list") {
    //   console.log(
    //     (await getPublicRoles(interaction.guild))
    //       .filter(
    //         (role) =>
    //           bot_role.position > role.position &&
    //           role != interaction.guild.roles.everyone
    //       )
    //       .map((role) => role.name)
    //   );
    // }

    // My Games.
    if (interaction.options.getSubcommand() === "my") {
      console.log(
        getRolesNames(
          filterPublicRoles(
            interaction,
            (interaction.member.roles as GuildMemberRoleManager).cache
          )
        )
      );
    }

    // Who Plays.
    if (interaction.options.getSubcommand() === "play") {
      let role = interaction.options.getRole("role") as Role;
      if (roleIsPublic(interaction, role)) {
        let members = (interaction.options.getRole("role") as Role).members;
        console.log(members.map((member) => `<@${member.user.id}>`));
      } else {
        // TODO: raise error
      }
    }

    // Join Game.
    if (interaction.options.getSubcommand() === "join") {
      let role = interaction.options.getRole("role") as Role;
      if (roleIsPublic(interaction, role)) {
        // TODO: add role.
      } else {
        // TODO: raise error.
      }
    }

    // Leave Game.
    if (interaction.options.getSubcommand() === "leave") {
      let role = interaction.options.getRole("role") as Role;
      if (roleIsPublic(interaction, role)) {
        // TODO: remove role.
      } else {
        // TODO: raise error.
      }
    }

    // console.log(interaction.options.get("my"));

    // const options = [];
    // for (const x of Array(100).keys()) {
    //   options.push({
    //     label: `Select me ${x}`,
    //     description: "This is a description",
    //     value: `option_${x}`,
    //   });
    // }

    await interaction.reply({
      content: "Pong11!",
      components: [
        // new MessageActionRow().addComponents([
        // new MessageButton()
        //   .setCustomId("primary")
        //   .setLabel("Primary")
        //   .setStyle("PRIMARY"),
        //   new MessageSelectMenu()
        //     .setCustomId("select")
        //     .setPlaceholder("Nothing selected")
        //     .addOptions(options),
        // ]),
      ],
    });
  },
};
