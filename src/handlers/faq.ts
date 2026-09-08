import type { CommandHandler } from "../context.ts";
import { ephemeralError } from "../discord.ts";
import { FAQ_ENTRIES } from "../faq_entries.ts";

export const faq: CommandHandler = async (interaction) => {
	const name = interaction.options.getSubcommand();
	const entry = FAQ_ENTRIES[name];
	if (!entry) {
		await interaction.reply(
			ephemeralError("Помилка", `Невідомий розділ ЧаПів: ${name}.`),
		);
		return;
	}
	await interaction.reply({
		embeds: [
			{
				title: entry.title,
				description: entry.description,
				...(entry.image && { image: { url: entry.image } }),
			},
		],
	});
};
