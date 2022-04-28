import { SlashCommandBuilder } from '@discordjs/builders';

import { MessageEmbed, Client } from 'discord.js';

// enum EmbedColor {
//   Primary = "#007bff",
//   Info = "#17a2b8",
//   Success = "#28a745",
//   Warning = "#ffc107",
//   Danger = "#dc3545",
// }

const items = [
  {
    name: 'ua-interface',
    description: 'Чому інтерфейс українською - це важливо?',
    embed: new MessageEmbed()
      .setTitle('Інтерфейс українською - це важливо! І ось чому:')
      .setDescription(
        `
        Розробники ПО та ігор послуговуються статистикою щодо використання мов інтерфейсу і приймають рішення в тому числі базуючись на ній щодо локалізації ігор та доступності мов.

        Приклад подібної статистики (секція "Language"): https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam

        Регіональна розбивка аудиторії відбувається в тому числі по мовній ознаці: часом, доходить до того що деякі ігри Ubisoft та EA певний час для України були недоступні англійською. Наприклад, Lost Ark та деякі інші ММО де нас по факту насильно загнали в ру регіон.

        Купа ігор доступні українською завдяки завдяки нашим перекладачам-волонтерам, які на то витратили купу власного часу. Один з найбільших таких проектів - Kingdom Come: Deliverance. Такі ініціативи варто підтримувати. І найкраща підтримка - грати українською. Зіграйте, не пошкодуєте!

        Чим більший буде відсоток користувачів україномовних інтерфейсів - тим більше їх буде доступно, і тим вища буде якість перекладу.
        `,
      ),
  },
];

export const builder = new SlashCommandBuilder()
  .setName('faq')
  .setDescription('ЧаПи');

items.forEach((record) =>
  builder.addSubcommand((subcommand) =>
    subcommand.setName(record.name).setDescription(record.description),
  ),
);

export function init(client: Client) {
  client.on('interactionCreate', async (interaction) => {
    // Command.
    if (interaction.isCommand() && interaction.commandName === builder.name) {
      const embed = items.find(
        (item) => item.name === interaction.options.getSubcommand(),
      ).embed;
      await interaction.reply({
        embeds: [embed],
      });
    }
  });
}
