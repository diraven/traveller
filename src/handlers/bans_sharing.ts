/**
 * Bans sharing across servers.
 *
 * A moderator bans someone however they like, then runs `/bans_sharing share`
 * (or right-clicks the user, "Apps", "Поширити бан"). The bot posts a notice
 * in every participating server's channel. Where the moderator is trusted the
 * ban is applied automatically; elsewhere moderators get "ban too" and
 * "ignore" buttons plus a copy-pasteable `/ban` command.
 *
 * Button clicks arrive as message component interactions. Everything they
 * need is read back from the embed fields, so no state is kept between the
 * post and the click.
 */
import {
  ButtonStyle,
  ComponentType,
  PermissionFlagsBits,
  type APIActionRowComponent,
  type APIComponentInMessageActionRow,
  type APIEmbed,
  type APIInteractionResponse,
  type APIUser,
} from "discord-api-types/v10";

import * as db from "../db.ts";
import {
  Color,
  DiscordAPIError,
  NO_ACCESS,
  avatarUrl,
  banMember,
  channelMention,
  createMessage,
  deferred,
  deferredUpdate,
  displayName,
  embedMessage,
  ephemeralError,
  errorEmbed,
  getAppGuildPermissions,
  getChannelOption,
  getGuild,
  getGuildId,
  getInvoker,
  getOptionalStringOption,
  getResolvedUser,
  getSubcommandName,
  getUserOption,
  hasPermission,
  isBanned,
  memberHasPermission,
  successEmbed,
  updateMessage,
  userFacingMessage,
  userMention,
  type CommandHandler,
  type ComponentHandler,
  type UserCommandHandler,
} from "../discord.ts";
import type { Env } from "../env.ts";

export const BAN_BUTTON_ID = "bans_sharing:ban";
export const SKIP_BUTTON_ID = "bans_sharing:skip";

const BANNED_FIELD = "Забанений";
const TARGET_ID_FIELD = "target_id";
const REASON_FIELD = "reason";
/**
 * Embed field values cannot be empty, so an absent reason needs a stand-in.
 * The zero-width space renders as nothing and cannot be typed by a moderator,
 * so a literal reason never collides with it.
 */
const NO_REASON = "​";

interface Ban {
  guildId: string;
  guildName: string;
  actor: APIUser;
  target: APIUser;
  reason: string | undefined;
}

function banEmbed(ban: Ban): APIEmbed {
  const embed: APIEmbed = {
    title: `Бан на сервері ${ban.guildName}`,
    fields: [
      { name: "Сервер", value: ban.guildName },
      {
        name: "Модератор",
        value: `${displayName(ban.actor)} '${ban.actor.username}'`,
      },
      {
        name: BANNED_FIELD,
        value: `${userMention(ban.target.id)} '${displayName(ban.target)}' '${ban.target.username}'`,
      },
      { name: "guild_id", value: ban.guildId },
      { name: "actor_id", value: ban.actor.id },
      { name: TARGET_ID_FIELD, value: ban.target.id },
      { name: REASON_FIELD, value: ban.reason || NO_REASON },
    ],
  };
  const thumbnail = avatarUrl(ban.target);
  if (thumbnail) {
    embed.thumbnail = { url: thumbnail };
  }
  return embed;
}

function embedField(embed: APIEmbed, name: string): string | undefined {
  return embed.fields?.find((field) => field.name === name)?.value;
}

function banButtons(
  disabled: boolean,
): APIActionRowComponent<APIComponentInMessageActionRow>[] {
  return [
    {
      type: ComponentType.ActionRow,
      components: [
        {
          type: ComponentType.Button,
          style: ButtonStyle.Danger,
          label: "Теж забанити",
          custom_id: BAN_BUTTON_ID,
          disabled,
        },
        {
          type: ComponentType.Button,
          style: ButtonStyle.Secondary,
          label: "Ігнорувати",
          custom_id: SKIP_BUTTON_ID,
          disabled,
        },
      ],
    },
  ];
}

function banCommandText(targetId: string, reason: string | undefined): string {
  // `delete_messages` is left empty on purpose: its values depend on the
  // moderator's interface language.
  return `/ban user:${targetId} delete_messages:${reason ? ` reason: ${reason}` : ""}`;
}

/**
 * Posts the ban to one participating server. Servers where the bot lacks Ban
 * Members get the copy-pasteable command instead of buttons that could only
 * fail, matching the two modes the gateway version documented.
 */
async function notifyGuild(
  env: Env,
  ban: Ban,
  destination: db.BansSharingChannel,
  canBan: boolean,
): Promise<void> {
  const embed = banEmbed(ban);
  embed.title = "Новий бан на іншому сервері";
  const content = embedField(embed, BANNED_FIELD);

  if (
    canBan &&
    (await db.isTrustedModerator(env.DB, destination.guild_id, ban.actor.id))
  ) {
    try {
      await banMember(env, destination.guild_id, ban.target.id, ban.reason);
      embed.description = `**Статус:** застосовано автоматично, довірений модератор ${displayName(ban.actor)} (${ban.actor.id})`;
      await createMessage(env, destination.channel_id, {
        content,
        embeds: [embed],
        components: banButtons(true),
      });
      return;
    } catch (error) {
      // Fall through to the manual flow when the ban is refused.
      console.error(error);
    }
  }

  embed.footer = {
    text: canBan
      ? "Якщо кнопки з якоїсь причини не працюють, скористайтеся командою нижче."
      : "У бота відсутні права на бан. Для створення такого самого бану на цьому сервері вам доведеться скопіювати та відправити текстову команду нижче.",
  };
  const posted = await createMessage(env, destination.channel_id, {
    content,
    embeds: [embed],
    // Buttons the bot could not act on would only ever fail.
    ...(canBan ? { components: banButtons(false) } : {}),
  });
  await createMessage(env, destination.channel_id, {
    content: banCommandText(ban.target.id, ban.reason),
    message_reference: { message_id: posted.id },
    flags: 4, // SUPPRESS_EMBEDS
  });
}

async function share(
  interaction:
    Parameters<CommandHandler>[0] | Parameters<UserCommandHandler>[0],
  env: Env,
  ctx: ExecutionContext,
  target: APIUser,
  reason: string | undefined,
): Promise<APIInteractionResponse> {
  if (!memberHasPermission(interaction, PermissionFlagsBits.BanMembers)) {
    return NO_ACCESS;
  }
  const guildId = getGuildId(interaction);
  const actor = getInvoker(interaction);

  const guild = await db.getGuild(env.DB, guildId);
  if (!guild?.bans_sharing_channel_id) {
    return ephemeralError(
      "Не налаштовано канал сповіщень.",
      "Налаштуйте канал сповіщень за допомогою команди `/bans_sharing set_channel`.",
    );
  }
  if (await db.hasSeenBan(env.DB, target.id)) {
    return ephemeralError(
      "Бан вже поширено",
      `Бан користувача ${userMention(target.id)} вже було поширено раніше.`,
    );
  }
  const channelId = guild.bans_sharing_channel_id;

  return deferred(interaction, env, ctx, async () => {
    // The gateway version could only ever fire on a real ban. Here the
    // moderator names the user, so confirm the ban exists before telling
    // other servers about it: trusting servers apply it automatically.
    if (!(await isBanned(env, guildId, target.id))) {
      return {
        embeds: [
          errorEmbed(
            "Користувача не забанено",
            `${userMention(target.id)} не забанений на цьому сервері. Спочатку забаньте його, потім поширюйте бан.`,
          ),
        ],
      };
    }

    const ban: Ban = {
      guildId,
      guildName: (await getGuild(env, guildId)).name,
      actor,
      target,
      reason,
    };

    const destinations = await db.listBansSharingChannels(env.DB, guildId);
    const appPermissions = await getAppGuildPermissions(env);
    let delivered = 0;
    for (const destination of destinations) {
      try {
        await notifyGuild(
          env,
          ban,
          destination,
          hasPermission(
            appPermissions.get(destination.guild_id)?.toString(),
            PermissionFlagsBits.BanMembers,
          ),
        );
        delivered += 1;
      } catch (error) {
        console.error(error);
      }
    }

    // Recorded only once the fan-out has run, so a failure before this point
    // leaves the ban shareable again rather than permanently marked seen.
    await db.recordBan(env.DB, target.id, actor.id, reason);

    // Local notice, so the originating server keeps a record too.
    const local = banEmbed(ban);
    local.title = "Новий бан на цьому сервері";
    local.description = `**Статус:** поширено на ${delivered} з ${destinations.length} серверів модератором ${userMention(actor.id)}`;
    await createMessage(env, channelId, {
      content: embedField(local, BANNED_FIELD),
      embeds: [local],
    });

    return {
      embeds: [
        successEmbed(
          "Бан поширено",
          `Сповіщення про бан ${userMention(target.id)} відправлено на ${delivered} з ${destinations.length} серверів.`,
        ),
      ],
    };
  });
}

const shareCommand: CommandHandler = (interaction, env, ctx) => {
  const targetId = getUserOption(interaction, "user");
  const target = getResolvedUser(interaction, targetId);
  if (!target) {
    return ephemeralError("Помилка", "Користувача не знайдено.");
  }
  return share(
    interaction,
    env,
    ctx,
    target,
    getOptionalStringOption(interaction, "reason"),
  );
};

export const shareBanUserCommand: UserCommandHandler = (
  interaction,
  env,
  ctx,
) => {
  const target = getResolvedUser(interaction, interaction.data.target_id);
  if (!target) {
    return ephemeralError("Помилка", "Користувача не знайдено.");
  }
  return share(interaction, env, ctx, target, undefined);
};

const setChannel: CommandHandler = (interaction, env, ctx) => {
  if (!memberHasPermission(interaction, PermissionFlagsBits.Administrator)) {
    return NO_ACCESS;
  }
  const channelId = getChannelOption(interaction, "channel");

  return deferred(interaction, env, ctx, async () => {
    try {
      await createMessage(env, channelId, {
        embeds: [
          {
            title: "Перевірка",
            description: `Тестове повідомлення для перевірки доступу до каналу сповіщень ${channelMention(channelId)}.`,
          },
        ],
      });
    } catch (error) {
      if (error instanceof DiscordAPIError) {
        return {
          embeds: [
            errorEmbed(
              "Відсутній доступ",
              `Відсутній доступ до каналу сповіщень ${channelMention(channelId)}, перевірте налаштування ролей.`,
            ),
          ],
        };
      }
      throw error;
    }

    await db.setBansSharingChannel(env.DB, getGuildId(interaction), channelId);
    return {
      embeds: [
        successEmbed(
          "Змінено канал сповіщень бота",
          `Новий канал сповіщень: ${channelMention(channelId)}`,
        ),
      ],
    };
  });
};

const checkConfig: CommandHandler = (interaction, env, ctx) => {
  if (!memberHasPermission(interaction, PermissionFlagsBits.Administrator)) {
    return NO_ACCESS;
  }
  const guildId = getGuildId(interaction);

  return deferred(interaction, env, ctx, async () => {
    const problems: [string, string][] = [];

    const guild = await db.getGuild(env.DB, guildId);
    if (guild?.bans_sharing_channel_id) {
      const channelId = guild.bans_sharing_channel_id;
      try {
        const posted = await createMessage(env, channelId, {
          embeds: [
            {
              title: "Перевірка",
              description: "Тестове повідомлення-вставка (embed).",
            },
          ],
        });
        await createMessage(env, channelId, {
          content: "Тестове текстове повідомлення.",
          message_reference: { message_id: posted.id },
        });
      } catch (error) {
        problems.push([
          `Не вдалося відправити повідомлення в канал ${channelMention(channelId)}.`,
          // Embed field values cannot be empty, and an error body can be.
          userFacingMessage(error),
        ]);
      }
    } else {
      problems.push([
        "Не налаштовано канал сповіщень.",
        "Налаштуйте канал сповіщень за допомогою команди `/bans_sharing set_channel`",
      ]);
    }

    const trusted = await db.listTrustedModerators(env.DB, guildId);
    const names = trusted.map(
      (moderator) => `${moderator.user_global_name} (${moderator.user_id})`,
    );

    return {
      embeds: [
        {
          title: "Результати перевірки налаштувань шарингу банів",
          description:
            problems.length === 0
              ? `Все ок.\nДовірені модератори: ${names.length ? names.join(", ") : "немає"}`
              : "Помилка. Необхідні наступні права для каналу сповіщень:\n* View Channel\n* Send Messages\n* Read Messages History\n* Embed Links",
          color: problems.length === 0 ? Color.green : Color.red,
          fields: problems.map(([name, value]) => ({
            name,
            value,
            inline: false,
          })),
        },
      ],
    };
  });
};

const addTrustedModerator: CommandHandler = async (interaction, env) => {
  if (!memberHasPermission(interaction, PermissionFlagsBits.BanMembers)) {
    return NO_ACCESS;
  }
  const userId = getUserOption(interaction, "user");
  const user = getResolvedUser(interaction, userId);
  if (!user) {
    return ephemeralError("Помилка", "Користувача не знайдено.");
  }
  const name = displayName(user);

  const added = await db.addTrustedModerator(env.DB, {
    guild_id: getGuildId(interaction),
    user_id: userId,
    user_global_name: name,
    created_by: getInvoker(interaction).id,
  });
  if (!added) {
    return embedMessage(
      errorEmbed(
        "Помилка",
        `Користувач ${name} вже є довіреним модератором на цьому сервері.`,
      ),
    );
  }
  return embedMessage(
    successEmbed(
      "Успішно",
      `Додано довіреного модератора: ${name}. За умови наявності відповідних дозволів у бота, бани цього модератора на інших серверах будуть автоматично застосовані і тут.`,
    ),
  );
};

const removeTrustedModerator: CommandHandler = async (interaction, env) => {
  if (!memberHasPermission(interaction, PermissionFlagsBits.BanMembers)) {
    return NO_ACCESS;
  }
  const userId = getUserOption(interaction, "user");
  const removed = await db.removeTrustedModerator(
    env.DB,
    getGuildId(interaction),
    userId,
  );
  if (!removed) {
    return embedMessage(
      errorEmbed(
        "Користувача не знайдено",
        `Користувач з ідентифікатором ${userId} не є довіреним модератором.`,
      ),
    );
  }
  return embedMessage(
    successEmbed(
      "Успішно",
      `Видалено модератора з довірених: ${removed.user_global_name}.`,
    ),
  );
};

export const bansSharing: CommandHandler = (interaction, env, ctx) => {
  switch (getSubcommandName(interaction)) {
    case "share":
      return shareCommand(interaction, env, ctx);
    case "set_channel":
      return setChannel(interaction, env, ctx);
    case "check_config":
      return checkConfig(interaction, env, ctx);
    case "add_trusted_moderator":
      return addTrustedModerator(interaction, env, ctx);
    case "remove_trusted_moderator":
      return removeTrustedModerator(interaction, env, ctx);
    default:
      return ephemeralError("Помилка", "Невідома команда.");
  }
};

// Buttons on ban notices in other servers.

export const banButton: ComponentHandler = (interaction, env, ctx) => {
  if (!memberHasPermission(interaction, PermissionFlagsBits.BanMembers)) {
    return NO_ACCESS;
  }
  const embed = interaction.message.embeds[0];
  const targetId = embed ? embedField(embed, TARGET_ID_FIELD) : undefined;
  if (!embed || !targetId) {
    return ephemeralError("Помилка", "Повідомлення не містить даних бану.");
  }
  const reasonField = embedField(embed, REASON_FIELD);
  const reason = reasonField === NO_REASON ? undefined : reasonField;

  // The ban is applied in the guild the button was clicked in, never the one
  // named in the embed: the embed is attacker-editable in principle, the
  // interaction's guild is signed by Discord.
  const guildId = getGuildId(interaction);

  // Banning can hit a rate limit, which would blow the 3-second deadline.
  return deferredUpdate(interaction, env, ctx, async () => {
    try {
      await banMember(env, guildId, targetId, reason);
    } catch (error) {
      if (error instanceof DiscordAPIError) {
        return {
          embeds: [
            {
              ...embed,
              description: `**Статус:** не вдалося забанити (Discord відповів ${error.status}). Перевірте права бота або скористайтеся текстовою командою нижче.`,
            },
          ],
          components: banButtons(false),
        };
      }
      throw error;
    }

    return {
      embeds: [
        {
          ...embed,
          description: `**Статус:** теж забанено модератором ${userMention(getInvoker(interaction).id)}.`,
        },
      ],
      components: banButtons(true),
    };
  });
};

export const skipButton: ComponentHandler = (interaction) => {
  if (!memberHasPermission(interaction, PermissionFlagsBits.BanMembers)) {
    return NO_ACCESS;
  }
  const embed = interaction.message.embeds[0] ?? {};
  return updateMessage({
    embeds: [
      {
        ...embed,
        description: `**Статус:** проігноровано модератором ${userMention(getInvoker(interaction).id)}`,
      },
    ],
    components: banButtons(true),
  });
};
