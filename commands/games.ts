import { roleMention, SlashCommandBuilder } from "@discordjs/builders";
import { arrayToPages } from "../pager";
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
} from "discord.js";
import { Command } from "../types/command";

// return new MessageEmbed()
// .setColor(embedTypeColor[this.type])
// .setTitle("Some title")
// .setURL("https://discord.js.org/")
// .setAuthor({
//   name: "Some name",
//   iconURL: "https://i.imgur.com/AfFp7pu.png",
//   url: "https://discord.js.org",
// })
// .setDescription("Some description here")
// .setThumbnail("https://i.imgur.com/AfFp7pu.png")
// .addFields(
//   { name: "Regular field title", value: "Some value here" },
//   { name: "\u200B", value: "\u200B" },
//   { name: "Inline field title", value: "Some value here", inline: true },
//   { name: "Inline field title", value: "Some value here", inline: true }
// )
// .addField("Inline field title", "Some value here", true)
// .setImage("https://i.imgur.com/AfFp7pu.png")
// .setTimestamp()
// .setFooter({
//   text: "Some footer text here",
//   iconURL: "https://i.imgur.com/AfFp7pu.png",
// });

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
    .setDescription("Ігри")
    // List.
    .addSubcommand((subcommand) =>
      subcommand.setName("list").setDescription("Список ігор")
    )

    // My.
    .addSubcommand((subcommand) =>
      subcommand.setName("my").setDescription("Мої ігри")
    )

    // Who.
    .addSubcommand((subcommand) =>
      subcommand
        .setName("play")
        .setDescription("Хто грає")
        .addRoleOption((option) =>
          option.setName("game").setDescription("Оберіть гру").setRequired(true)
        )
    )

    // Join.
    .addSubcommand((subcommand) =>
      subcommand
        .setName("join")
        .setDescription("Долучитися")
        .addRoleOption((option) =>
          option.setName("role").setDescription("Оберіть гру").setRequired(true)
        )
    )

    // Leave.
    .addSubcommand((subcommand) =>
      subcommand
        .setName("leave")
        .setDescription("Покинути гру")
        .addRoleOption((option) =>
          option.setName("role").setDescription("Оберіть гру").setRequired(true)
        )
    ),

  execute: async function execute(interaction: CommandInteraction) {
    // List.
    if (interaction.options.getSubcommand() === "list") {
      console.log(
        arrayToPages(
          getRolesNames(
            filterPublicRoles(
              interaction,
              await interaction.guild.roles.fetch()
            )
          )
        )
      );

      interaction.reply({
        ephemeral: true,
        embeds: [
          new MessageEmbed()
            .setColor(EmbedColor.Primary)
            .setTitle("Ігрові ролі")
            .setURL("https://github.com/diraven/traveller")
            .setDescription("Some description here")
            .setTimestamp(),
        ],
      });
    }

    // My.

    // Who.

    // Join.

    // Leave.

    // My Games.
    // if (interaction.options.getSubcommand() === "my") {
    //   console.log(
    //     getRolesNames(
    //       filterPublicRoles(
    //         interaction,
    //         (interaction.member.roles as GuildMemberRoleManager).cache
    //       )
    //     )
    //   );
    // }

    // // Who Plays.
    // if (interaction.options.getSubcommand() === "play") {
    //   let role = interaction.options.getRole("role") as Role;
    //   if (roleIsPublic(interaction, role)) {
    //     let members = (interaction.options.getRole("role") as Role).members;
    //     console.log(members.map((member) => `<@${member.user.id}>`));
    //   } else {
    //     // TODO: raise error
    //   }
    // }

    // // Join Game.
    // if (interaction.options.getSubcommand() === "join") {
    //   let role = interaction.options.getRole("role") as Role;
    //   if (roleIsPublic(interaction, role)) {
    //     // TODO: add role.
    //   } else {
    //     // TODO: raise error.
    //   }
    // }

    // // Leave Game.
    // if (interaction.options.getSubcommand() === "leave") {
    //   let role = interaction.options.getRole("role") as Role;
    //   if (roleIsPublic(interaction, role)) {
    //     // TODO: remove role.
    //   } else {
    //     // TODO: raise error.
    //   }
    // }

    // console.log(interaction.options.get("my"));

    // const options = [];
    // for (const x of Array(100).keys()) {
    //   options.push({
    //     label: `Select me ${x}`,
    //     description: "This is a description",
    //     value: `option_${x}`,
    //   });
    // }

    // await interaction.reply({
    //   content: "Pong11!",
    //   components: [
    //     new MessageActionRow().addComponents([
    //       new MessageButton()
    //         .setCustomId("primary")
    //         .setLabel("Primary")
    //         .setStyle("PRIMARY"),
    //       //   new MessageSelectMenu()
    //       //     .setCustomId("select")
    //       //     .setPlaceholder("Шо по русні?")
    //       //     .addOptions([
    //       //       {
    //       //         label: "Не всьо так однозначно.",
    //       //         value: "not_ok1",
    //       //       },
    //       //       {
    //       //         label: "Я вне палітікі!.",
    //       //         value: "not_ok2",
    //       //       },
    //       //       {
    //       //         label: "Какаяразніца!",
    //       //         value: "not_ok3",
    //       //       },
    //       //       {
    //       //         label: "Русні пизда!",
    //       //         value: "ok",
    //       //       },
    //       //     ]),
    //     ]),
    //   ],
    // });
  },
};
