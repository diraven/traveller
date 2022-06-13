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
        Розробники ПО та ігор послуговуються статистикою щодо використання мов інтерфейсу і приймають рішення в тому числі базуючись на ній щодо локалізації ігор та доступності мов. В тому числі і українські студії.

        Приклад подібної статистики (секція "Language"): https://store.steampowered.com/hwsurvey/Steam-Hardware-Software-Survey-Welcome-to-Steam

        Регіональний поділ аудиторії відбувається в тому числі за мовою: доходило до того, що деякі ігри Ubisoft та EA певний час були недоступні англійською для України. А в Lost Ark та деяких інших ММО нас взагалі насильно загнали в ру регіон без права вибору.

        Купа ігор доступні українською завдяки нашим перекладачам-волонтерам, які на то витрачають купу власного часу. Kingdom Come: Deliverance, Satisfactory, Deep Rock Galactic, Factorio. Такі ініціативи варто підтримувати. І найкраща підтримка - грати українською. Зіграйте, не пошкодуєте!

        Зі зростанням кількості користувачів україномовного інтерфейсу зростатимуть, відповідно, кількість і якість локалізацій. Й тим швидше вони з'являтимуться. Можливо, з часом, навіть на релізі!
        `,
      ),
  },
  {
    name: 'apolitical',
    description: 'Поза політикою?',
    embed: new MessageEmbed()
      .setTitle('"Поза політикою" не буває, і ось чому:')
      .setDescription(
        `
        Політика - це діяльність, спрямована на управління державою. Законодавство - це політика. Закони визначають правила нашого з вами життя та взаємодії в суспільстві. А тому політика - це все. Медицина, освіта, ціна ковбаси в магазині чи роздовбана дорога - це політика. Ваше авто, чай на сніданок і хліб з маслом - це політика. Ваш (не)спокійний сон та вибухи за вікном - теж політика. Спорт в будь-яких його проявах - теж політика, як частина суспільного життя. Від політики нікуди не дітися і не сховатися, вона всюди.

        Тому сентенції на кшталт "ігри поза політикою" чи "спорт поза політикою" щонайменше неправдиві. Щонайбільше - небезпечні. Люди, що позиціонують себе "поза політикою", свідомо відмовляються від відповідальності за власне життя і майбутнє, віддаючи його в руки тих, хто "в політиці". Вибір за вас зробить інший, а з наслідками цього вибору доведеться жити вам.

        Тому політика - це важливо. Брати в ній участь і впливати на суспільні процеси - теж важливо. Писати листи, запити, вимагати дотримання своїх прав і свобод. Джерелом влади в Україні є народ. Суспільний запит визначає курс держави. І починається з окремих людей та простих дій.
        `,
      ),
  },
  {
    name: 'svc',
    description: 'Що таке СВЦ?',
    embed: new MessageEmbed()
      .setTitle('СВЦ, Синдром Великого Цабе:')
      .setDescription(
        `
        Морально-психологічний стан, що характеризується надмірним почуттям власної важливості.
        
        **Групи ризику:** лідери думок, публічні люди, люди що мають певну владу.
        **Ускладнення:**  гостра форма має тенденцію до переходу в хронічну з плином часу, що, в свою чергу, може призвести до егоцентризму та нарцисизму. Наявний егоцентризм та/або нарцисизм ускладнює перебіг синдрому та прискорює перехід синдрому в хронічну форму.
        **Лікування:** зняти корону. Можливе симптоматичне лікування фейспалмами. У випадку рецидивів: призначити підтримуючу терапію - суспільно корисні роботи.
        `,
      ),
  },
  {
    name: 'lfg',
    description: 'Як знайти гравців для гри разом?',
    embed: new MessageEmbed().setTitle('Пошук гравців:').setDescription(
      `
        Оберіть канал <#243720639226183680>, а в ньому гілку відповідної гри. В гілці і шукайте однодумців. Якщо гілки вашої гри не існує - зверніться до людей з роллю <@&285029616035299328> для її створення.

        Гіфка нижче показує як шукати гілки.
        
        https://support.discord.com/hc/article_attachments/4405266120471/thread_popout_demo.gif
        `,
    ),
  },
  {
    name: 'spoiler',
    description: 'Як сховати фото на тілібоні під спойлер',
    embed: new MessageEmbed().setTitle('Спойлер на тілібоні').setDescription(
      `
      1. Після того як ви обрали фото, тицьніть кніпку назад на тілібоні, щоб закрити вікно з галереєю(рис. 1).

      2. Тицьніть на обране фото на вікні вкладень ще раз(рис. 2).

      3. Тицьніть на позначку "позначити як спойлер"(рис. 3).
      
      Вуаля, спойлер на тілібоні. Не так вже й складно, е?

      https://cdn.discordapp.com/attachments/233896169309339649/983009206015787068/IMG_20220605_170655.jpg
      https://cdn.discordapp.com/attachments/233896169309339649/983009206384877588/IMG_20220605_170712.jpg
      https://cdn.discordapp.com/attachments/233896169309339649/983009206724599858/IMG_20220605_170728.jpg
      `,
    ),
  },
];

export const builder = new SlashCommandBuilder()
  .setName('faq')
  .setDescription('ЧаПи.');

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
