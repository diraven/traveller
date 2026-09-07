import {
	type CommandHandler,
	embedMessage,
	ephemeralError,
	getSubcommandName,
} from "../discord.ts";
import { FAQ_ENTRIES } from "../faq_entries.ts";

export const faq: CommandHandler = (interaction) => {
	const name = getSubcommandName(interaction);
	const entry = name ? FAQ_ENTRIES[name] : undefined;
	if (!entry) {
		return ephemeralError("Помилка", `Невідомий розділ ЧаПів: ${name}.`);
	}
	return embedMessage({
		title: entry.title,
		description: entry.description,
		...(entry.image && { image: { url: entry.image } }),
	});
};
