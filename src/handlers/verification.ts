import {
	type APIEmbed,
	DiscordAPIError,
	PermissionFlagsBits,
	roleMention,
	userMention,
} from "discord.js";

import type { CommandHandler } from "../context.ts";
import * as db from "../db.ts";
import {
	Color,
	ephemeralError,
	errorEmbed,
	NO_ACCESS,
	successEmbed,
} from "../discord.ts";

type Problem = [problem: string, suggestion: string];

function report(title: string, problems: Problem[]): APIEmbed {
	return {
		title,
		description: problems.length === 0 ? "Все ок." : "",
		color: problems.length === 0 ? Color.green : Color.red,
		fields: problems.map(([name, value]) => ({ name, value, inline: false })),
	};
}

const setRole: CommandHandler = async (interaction, ctx) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.Administrator)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	const role = interaction.options.getRole("role", true);
	await db.setVerificationRole(ctx.db, interaction.guildId, role.id);
	await interaction.reply({
		embeds: [
			successEmbed(
				"Змінено роль верифікації",
				`Нова роль верифікації: ${roleMention(role.id)}`,
			),
		],
	});
};

const checkConfig: CommandHandler = async (interaction, ctx) => {
	if (!interaction.memberPermissions.has(PermissionFlagsBits.Administrator)) {
		await interaction.reply(NO_ACCESS);
		return;
	}
	await interaction.deferReply();

	const problems: Problem[] = [];
	const { guild } = interaction;
	const me = await guild.members.fetchMe();

	// Guild-wide, not the channel's effective permissions: Manage Roles is
	// channel-overridable, and what matters is whether the bot holds it at all.
	if (!me.permissions.has(PermissionFlagsBits.ManageRoles)) {
		problems.push([
			"Відсутній дозвіл на управління ролями.",
			"Надайте боту доступ до управління ролями.",
		]);
	}

	const stored = await db.getGuild(ctx.db, interaction.guildId);
	if (!stored?.verification_role_id) {
		problems.push([
			"Роль верифікації не задана.",
			"Вкажіть роль верифікації для бота за допомогою команди `/verification set_role`.",
		]);
	} else {
		const role = await guild.roles.fetch(stored.verification_role_id);
		if (!role) {
			problems.push([
				"Роль верифікації не знайдено.",
				"Роль видалено. Вкажіть нову за допомогою `/verification set_role`.",
			]);
		} else if (role.position >= me.roles.highest.position) {
			// The bot can only hand out roles positioned below its highest role.
			problems.push([
				`Відсутній дозвіл для видачі ролі ${roleMention(role.id)}.`,
				"Перевірте щоб роль була розташована нижче ролі бота.",
			]);
		}
	}

	await interaction.editReply({
		embeds: [report("Результати перевірки налаштувань верифікації", problems)],
	});
};

export const verification: CommandHandler = async (interaction, ctx) => {
	switch (interaction.options.getSubcommand()) {
		case "set_role":
			return setRole(interaction, ctx);
		case "check_config":
			return checkConfig(interaction, ctx);
		default:
			await interaction.reply(ephemeralError("Помилка", "Невідома команда."));
	}
};

export const verify: CommandHandler = async (interaction, ctx) => {
	const actor = interaction.user;
	const target = interaction.options.getUser("member", true);

	if (target.id === actor.id) {
		await interaction.reply({
			embeds: [
				errorEmbed(
					"???",
					"Самоверифікацією... кхм-кхм... краще займатися деінде.",
				),
			],
		});
		return;
	}
	if (target.id === interaction.client.user.id) {
		await interaction.reply({ embeds: [errorEmbed("???", "А мене за шо?)")] });
		return;
	}

	const configError = errorEmbed(
		"Помилка",
		"Скористайтесь командою `/verification check_config` (тільки для адміністраторів) для налаштування верифікації.",
	);
	const stored = await db.getGuild(ctx.db, interaction.guildId);
	const roleId = stored?.verification_role_id;
	if (!roleId) {
		await interaction.reply({ embeds: [configError] });
		return;
	}

	if (!interaction.member.roles.cache.has(roleId)) {
		await interaction.reply({
			embeds: [
				errorEmbed(
					"Помилка",
					"Тільки верифіковані користувачі можуть верифікувати інших.",
				),
			],
		});
		return;
	}

	const member = interaction.options.getMember("member");
	if (!member) {
		await interaction.reply({
			embeds: [
				errorEmbed("Помилка", "Користувача не знайдено на цьому сервері."),
			],
		});
		return;
	}
	if (member.roles.cache.has(roleId)) {
		await interaction.reply({
			embeds: [
				errorEmbed(
					"Помилка",
					`Користувача ${userMention(target.id)} вже верифіковано.`,
				),
			],
		});
		return;
	}

	// Granting a role can hit a rate limit, which would blow the three-second
	// deadline, so everything past the cheap guards runs deferred.
	await interaction.deferReply();
	try {
		await member.roles.add(
			roleId,
			`${userMention(actor.id)} '${actor.username}' (${actor.id})`,
		);
	} catch (error) {
		if (error instanceof DiscordAPIError) {
			console.error(error);
			await interaction.editReply({ embeds: [configError] });
			return;
		}
		throw error;
	}

	await interaction.editReply({
		embeds: [
			successEmbed(
				"Верифікація",
				`${userMention(actor.id)} верифікує ${userMention(target.id)} відкриваючи доступ до голосових каналів, постингу посилань, картинок та ін.`,
			),
		],
	});
};
