import { PermissionFlagsBits, type APIEmbed } from "discord-api-types/v10";

import * as db from "../db.ts";
import {
  Color,
  DiscordAPIError,
  NO_ACCESS,
  addMemberRole,
  deferred,
  embedMessage,
  ephemeralError,
  errorEmbed,
  getAppGuildPermissions,
  getGuildId,
  getGuildMember,
  getGuildRoles,
  getInvoker,
  getResolvedMember,
  getRoleOption,
  getSubcommandName,
  getUserOption,
  hasPermission,
  memberHasPermission,
  roleMention,
  successEmbed,
  userMention,
  type CommandHandler,
} from "../discord.ts";

type Problem = [problem: string, suggestion: string];

function report(title: string, problems: Problem[]): APIEmbed {
  const embed: APIEmbed = {
    title,
    description: problems.length === 0 ? "Все ок." : "",
    color: problems.length === 0 ? Color.green : Color.red,
    fields: problems.map(([name, value]) => ({ name, value, inline: false })),
  };
  return embed;
}

const setRole: CommandHandler = async (interaction, env) => {
  if (!memberHasPermission(interaction, PermissionFlagsBits.Administrator)) {
    return NO_ACCESS;
  }
  const roleId = getRoleOption(interaction, "role");
  await db.setVerificationRole(env.DB, getGuildId(interaction), roleId);
  return embedMessage(
    successEmbed(
      "Змінено роль верифікації",
      `Нова роль верифікації: ${roleMention(roleId)}`,
    ),
  );
};

const checkConfig: CommandHandler = (interaction, env, ctx) => {
  if (!memberHasPermission(interaction, PermissionFlagsBits.Administrator)) {
    return NO_ACCESS;
  }
  const guildId = getGuildId(interaction);

  return deferred(interaction, env, ctx, async () => {
    const problems: Problem[] = [];

    // Guild-wide, not the interaction's `app_permissions`: Manage Roles is
    // channel-overridable, and what matters is whether the bot holds it at
    // all, not whether this particular channel grants it.
    const appPermissions = await getAppGuildPermissions(env);
    if (
      !hasPermission(
        appPermissions.get(guildId)?.toString(),
        PermissionFlagsBits.ManageRoles,
      )
    ) {
      problems.push([
        "Відсутній дозвіл на управління ролями.",
        "Надайте боту доступ до управління ролями.",
      ]);
    }

    const guild = await db.getGuild(env.DB, guildId);
    if (!guild?.verification_role_id) {
      problems.push([
        "Роль верифікації не задана.",
        "Вкажіть роль верифікації для бота за допомогою команди `/verification set_role`.",
      ]);
    } else {
      const roles = await getGuildRoles(env, guildId);
      const role = roles.find(
        (candidate) => candidate.id === guild.verification_role_id,
      );
      if (!role) {
        problems.push([
          "Роль верифікації не знайдено.",
          "Роль видалено. Вкажіть нову за допомогою `/verification set_role`.",
        ]);
      } else {
        // The bot can only hand out roles positioned below its highest role.
        const bot = await getGuildMember(
          env,
          guildId,
          env.DISCORD_APPLICATION_ID,
        );
        const botTop = Math.max(
          0,
          ...roles
            .filter((candidate) => bot.roles.includes(candidate.id))
            .map((candidate) => candidate.position),
        );
        if (role.position >= botTop) {
          problems.push([
            `Відсутній дозвіл для видачі ролі ${roleMention(role.id)}.`,
            "Перевірте щоб роль була розташована нижче ролі бота.",
          ]);
        }
      }
    }

    return {
      embeds: [
        report("Результати перевірки налаштувань верифікації", problems),
      ],
    };
  });
};

export const verification: CommandHandler = (interaction, env, ctx) => {
  switch (getSubcommandName(interaction)) {
    case "set_role":
      return setRole(interaction, env, ctx);
    case "check_config":
      return checkConfig(interaction, env, ctx);
    default:
      return ephemeralError("Помилка", "Невідома команда.");
  }
};

export const verify: CommandHandler = async (interaction, env, ctx) => {
  const guildId = getGuildId(interaction);
  const actor = getInvoker(interaction);
  const targetId = getUserOption(interaction, "member");

  if (targetId === actor.id) {
    return embedMessage(
      errorEmbed(
        "???",
        "Самоверифікацією... кхм-кхм... краще займатися деінде.",
      ),
    );
  }
  if (targetId === env.DISCORD_APPLICATION_ID) {
    return embedMessage(errorEmbed("???", "А мене за шо?)"));
  }

  const configError = errorEmbed(
    "Помилка",
    "Скористайтесь командою `/verification check_config` (тільки для адміністраторів) для налаштування верифікації.",
  );
  const guild = await db.getGuild(env.DB, guildId);
  const roleId = guild?.verification_role_id;
  if (!roleId) {
    return embedMessage(configError);
  }

  if (!interaction.member?.roles.includes(roleId)) {
    return embedMessage(
      errorEmbed(
        "Помилка",
        "Тільки верифіковані користувачі можуть верифікувати інших.",
      ),
    );
  }

  const target = getResolvedMember(interaction, targetId);
  if (!target) {
    return embedMessage(
      errorEmbed("Помилка", "Користувача не знайдено на цьому сервері."),
    );
  }
  if (target.roles.includes(roleId)) {
    return embedMessage(
      errorEmbed(
        "Помилка",
        `Користувача ${userMention(targetId)} вже верифіковано.`,
      ),
    );
  }

  // Granting a role can hit a rate limit, which would blow the 3-second
  // deadline, so everything past the cheap guards runs deferred.
  return deferred(interaction, env, ctx, async () => {
    try {
      await addMemberRole(
        env,
        guildId,
        targetId,
        roleId,
        `${userMention(actor.id)} '${actor.username}' (${actor.id})`,
      );
    } catch (error) {
      if (error instanceof DiscordAPIError) {
        console.error(error);
        return { embeds: [configError] };
      }
      throw error;
    }

    return {
      embeds: [
        successEmbed(
          "Верифікація",
          `${userMention(actor.id)} верифікує ${userMention(targetId)} відкриваючи доступ до голосових каналів, постингу посилань, картинок та ін.`,
        ),
      ],
    };
  });
};
