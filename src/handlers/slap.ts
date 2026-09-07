import {
	Color,
	type CommandHandler,
	embedMessage,
	getInvoker,
	getUserOption,
	userMention,
} from "../discord.ts";

/** `{actor}` and `{target}` are replaced with user mentions. */
export const SLAP_TEMPLATES = [
	"{actor} прикладає {target} по спині величезним сомом.",
	"{actor} демонструє {target} щорічну заяву Арестовича на звільнення.",
	"{actor} щось кричить {target} на вухо.",
	"{actor} уважно дивиться {target} в очі.",
	"{actor} хизується електрохарчуванням перед {target}.",
	'{actor} шепоче {target} на вухо "русні пизда".',
	"{actor} шепоче {target} на вухо що стало краще.",
	"{actor} шепоче {target} на вухо що стало гірше.",
	'{actor} показує {target} пальцем на напис "зрада".',
	'{actor} показує {target} пальцем на напис "перемога".',
	'{actor} показує {target} пальцем на напис "переможна зрада".',
	'{actor} показує {target} пальцем на напис "зраджена перемога".',
	'{actor} показує {target} пальцем на напис "зрадоперемога".',
	"{actor} підозріло зиркає на {target}.",
	"{actor} тихенько ліпить слоупока {target} на спину.",
	"{actor} бідкається, {target} розводить руками.",
	'{actor} каже {target} "Це ж було вже!".',
	"{actor} вмовляє {target} проголосувати за Ляшка.",
	"{actor} демонструє свої музичні здібності. {target} плаче.",
	"{actor} демонструє свої вокальні здібності. {target} плаче.",
	'{actor} демонструє супер сайян. {target} каже "ок".',
	"{actor} конем б'є короля у {target}. Це гол.",
	"{actor} п'є чай з молоком. {target} каже що це мєрзость.",
	"{actor} робить {target} комплімент. Це надзвичайно ефективно!",
	"{actor} обіймає {target}. Всі інші заздрять.",
	"{actor} нагадує {target} що пора на завод.",
	"{actor} пропонує {target} виміряти довжину мосту.",
	"{actor} пропонує {target} розкрутитися.",
	"{actor} slaps {target} around with small 50Lbs Linux manual.",
	"{actor} пропонує {target} зупинитися і послухати.",
	"{actor} просить {target} покликати його мішок з м'ясом.",
] as const;

export function renderSlap(
	template: string,
	actorId: string,
	targetId: string,
): string {
	return template
		.replace("{actor}", userMention(actorId))
		.replace("{target}", userMention(targetId));
}

export const slap: CommandHandler = (interaction) => {
	const template =
		SLAP_TEMPLATES[Math.floor(Math.random() * SLAP_TEMPLATES.length)] ??
		SLAP_TEMPLATES[0];
	return embedMessage({
		title: "Йой!",
		description: renderSlap(
			template,
			getInvoker(interaction).id,
			getUserOption(interaction, "member"),
		),
		color: Color.blue,
	});
};
