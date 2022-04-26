import { Message, MessageEmbed } from "discord.js";

const maxPageLength = 4000;
const separator = " **|** ";

export function itemsArrayToPages(
  array: Array<string>,
  title: string = ""
): Array<MessageEmbed> {
  let pages: Array<MessageEmbed> = [];

  let embed = new MessageEmbed().setTitle(title).setDescription("");

  array.forEach((item) => {
    if (
      embed.description.length + separator.length + item.length <=
      maxPageLength
    ) {
      if (embed.description === "") {
        embed.description = item;
      } else {
        embed.description = embed.description + separator + item;
      }
    } else {
      pages.push(embed);
      embed = new MessageEmbed().setTitle(title).setDescription("");
      embed.description = item;
    }
  });

  if (embed.description !== "") {
    pages.push(embed);
  }

  return pages;
}
