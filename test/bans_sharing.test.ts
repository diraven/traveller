import { env } from "cloudflare:test";
import {
	type APIActionRowComponent,
	type APIButtonComponentWithCustomId,
	type APIComponentInMessageActionRow,
	type APIEmbed,
	type APIInteractionResponseChannelMessageWithSource,
	type APIInteractionResponseUpdateMessage,
	ButtonStyle,
	ComponentType,
	InteractionResponseType,
	MessageFlags,
	PermissionFlagsBits,
} from "discord-api-types/v10";
import { beforeAll, describe, expect, it } from "vitest";

import * as db from "../src/db.ts";
import { Color } from "../src/discord.ts";
import { BAN_BUTTON_ID, SKIP_BUTTON_ID } from "../src/handlers/bans_sharing.ts";
import {
	discordApi,
	dispatch,
	firstEmbed,
	type RecordedRequest,
} from "./harness.ts";
import {
	buttonInteraction,
	CHANNEL_ID,
	channelOption,
	chatInputInteraction,
	createSigner,
	GUILD_ID,
	INVOKER_ID,
	resolvedMember,
	type Signer,
	stringOption,
	subcommand,
	TARGET_ID,
	user,
	userCommandInteraction,
	userOption,
} from "./helpers.ts";

const OTHER_GUILD = "666666666666666666";
const OTHER_CHANNEL = "666666666666666001";
const TRUSTING_GUILD = "777777777777777777";
const TRUSTING_CHANNEL = "777777777777777001";
const MODERATOR = { permissions: PermissionFlagsBits.BanMembers };
const ADMIN = { permissions: PermissionFlagsBits.Administrator };

let signer: Signer;

beforeAll(async () => {
	signer = await createSigner();
});

function asMessage(body: unknown) {
	return body as APIInteractionResponseChannelMessageWithSource;
}

function bansSharing(
	name: string,
	options: Parameters<typeof subcommand>[1] = [],
	overrides: Parameters<typeof chatInputInteraction>[2] = MODERATOR,
) {
	return chatInputInteraction(
		"bans_sharing",
		[subcommand(name, options)],
		overrides,
	);
}

const targetUser = user(TARGET_ID, "troll");
const resolvedTarget = {
	users: { [TARGET_ID]: targetUser },
	members: { [TARGET_ID]: resolvedMember() },
};

/** A posted message: `POST /channels/{id}/messages` returning an id. */
function postedMessage(recorded: RecordedRequest) {
	return { id: `msg-${recorded.path.split("/")[2]}` };
}

/** `GET /users/@me/guilds`, giving the bot Ban Members in `banIn`. */
function appGuilds(banIn: string[]) {
	return {
		"GET /users/@me/guilds?limit=200": [
			GUILD_ID,
			OTHER_GUILD,
			TRUSTING_GUILD,
		].map((id) => ({
			id,
			permissions: (banIn.includes(id)
				? PermissionFlagsBits.BanMembers
				: PermissionFlagsBits.SendMessages
			).toString(),
		})),
	};
}

describe("/bans_sharing set_channel", () => {
	const setChannel = (overrides = ADMIN) =>
		bansSharing(
			"set_channel",
			[channelOption("channel", CHANNEL_ID)],
			overrides,
		);

	it("refuses non-administrators", async () => {
		const { body, requests } = await dispatch(signer, setChannel(MODERATOR));
		expect(requests).toEqual([]);
		expect(asMessage(body).data.flags).toBe(MessageFlags.Ephemeral);
	});

	it("posts a test message and stores the channel", async () => {
		const { edited, requests } = await dispatch(
			signer,
			setChannel(),
			discordApi({ [`POST /channels/${CHANNEL_ID}/messages`]: postedMessage }),
		);
		expect(requests).toHaveLength(1);
		expect(firstEmbed(requests[0]?.body as { embeds: APIEmbed[] }).title).toBe(
			"Перевірка",
		);
		expect(firstEmbed(edited).description).toBe(
			`Новий канал сповіщень: <#${CHANNEL_ID}>`,
		);
		expect(await db.getGuild(env.DB, GUILD_ID)).toMatchObject({
			bans_sharing_channel_id: CHANNEL_ID,
		});
	});

	it("reports a channel the bot cannot post into and keeps the old setting", async () => {
		const { edited } = await dispatch(
			signer,
			setChannel(),
			discordApi({
				[`POST /channels/${CHANNEL_ID}/messages`]: new Response(
					'{"message":"Missing Access"}',
					{ status: 403 },
				),
			}),
		);
		expect(firstEmbed(edited).title).toBe("Відсутній доступ");
		expect(await db.getGuild(env.DB, GUILD_ID)).toBeNull();
	});
});

describe("/bans_sharing trusted moderators", () => {
	const trusted = (name: string) =>
		bansSharing("add_trusted_moderator", [userOption("user", TARGET_ID)], {
			...MODERATOR,
			resolved: { users: { [TARGET_ID]: user(TARGET_ID, name) } },
		});

	it("adds a moderator once", async () => {
		const first = await dispatch(signer, trusted("mod"));
		expect(firstEmbed(asMessage(first.body).data).description).toContain(
			"Додано довіреного модератора: Mod.",
		);
		expect(await db.listTrustedModerators(env.DB, GUILD_ID)).toMatchObject([
			{ user_id: TARGET_ID, user_global_name: "Mod", created_by: INVOKER_ID },
		]);

		const second = await dispatch(signer, trusted("mod"));
		expect(firstEmbed(asMessage(second.body).data).description).toBe(
			"Користувач Mod вже є довіреним модератором на цьому сервері.",
		);
	});

	it("removes a moderator and reports unknown ones", async () => {
		await dispatch(signer, trusted("mod"));
		const remove = bansSharing("remove_trusted_moderator", [
			userOption("user", TARGET_ID),
		]);

		const removed = await dispatch(signer, remove);
		expect(firstEmbed(asMessage(removed.body).data).description).toBe(
			"Видалено модератора з довірених: Mod.",
		);
		expect(await db.listTrustedModerators(env.DB, GUILD_ID)).toEqual([]);

		const again = await dispatch(signer, remove);
		expect(firstEmbed(asMessage(again.body).data).title).toBe(
			"Користувача не знайдено",
		);
	});

	it("requires Ban Members", async () => {
		const { body } = await dispatch(
			signer,
			bansSharing("add_trusted_moderator", [userOption("user", TARGET_ID)], {}),
		);
		expect(asMessage(body).data.flags).toBe(MessageFlags.Ephemeral);
	});
});

describe("/bans_sharing check_config", () => {
	it("reports a missing channel", async () => {
		const { edited, requests } = await dispatch(
			signer,
			bansSharing("check_config", [], ADMIN),
		);
		expect(requests).toEqual([]);
		const embed = firstEmbed(edited);
		expect(embed.color).toBe(Color.red);
		expect(embed.fields).toMatchObject([
			{ name: "Не налаштовано канал сповіщень." },
		]);
	});

	it("posts test messages and lists trusted moderators", async () => {
		await db.setBansSharingChannel(env.DB, GUILD_ID, CHANNEL_ID);
		await db.addTrustedModerator(env.DB, {
			guild_id: GUILD_ID,
			user_id: TARGET_ID,
			user_global_name: "Mod",
			created_by: INVOKER_ID,
		});
		const { edited, requests } = await dispatch(
			signer,
			bansSharing("check_config", [], ADMIN),
			discordApi({ [`POST /channels/${CHANNEL_ID}/messages`]: postedMessage }),
		);
		expect(requests).toHaveLength(2);
		expect(requests[1]?.body).toMatchObject({
			content: "Тестове текстове повідомлення.",
			message_reference: { message_id: `msg-${CHANNEL_ID}` },
		});
		const embed = firstEmbed(edited);
		expect(embed.color).toBe(Color.green);
		expect(embed.description).toBe(
			`Все ок.\nДовірені модератори: Mod (${TARGET_ID})`,
		);
	});
});

describe("/bans_sharing share", () => {
	const share = (reason?: string) =>
		bansSharing(
			"share",
			[
				userOption("user", TARGET_ID),
				...(reason ? [stringOption("reason", reason)] : []),
			],
			{ ...MODERATOR, resolved: resolvedTarget },
		);

	async function configureNetwork() {
		await db.setBansSharingChannel(env.DB, GUILD_ID, CHANNEL_ID);
		await db.setBansSharingChannel(env.DB, OTHER_GUILD, OTHER_CHANNEL);
		await db.setBansSharingChannel(env.DB, TRUSTING_GUILD, TRUSTING_CHANNEL);
		await db.addTrustedModerator(env.DB, {
			guild_id: TRUSTING_GUILD,
			user_id: INVOKER_ID,
			user_global_name: "Invoker",
			created_by: "someone",
		});
	}

	const network = ({
		banStatus = 204,
		bannedLocally = true,
		canBanIn = [OTHER_GUILD, TRUSTING_GUILD],
	} = {}) =>
		discordApi({
			[`GET /guilds/${GUILD_ID}/bans/${TARGET_ID}`]: new Response(
				bannedLocally ? '{"user":{"id":"444444444444444444"}}' : "{}",
				{ status: bannedLocally ? 200 : 404 },
			),
			[`GET /guilds/${GUILD_ID}`]: { id: GUILD_ID, name: "Home" },
			...appGuilds(canBanIn),
			[`POST /channels/${CHANNEL_ID}/messages`]: postedMessage,
			[`POST /channels/${OTHER_CHANNEL}/messages`]: postedMessage,
			[`POST /channels/${TRUSTING_CHANNEL}/messages`]: postedMessage,
			[`PUT /guilds/${TRUSTING_GUILD}/bans/${TARGET_ID}`]: new Response(
				banStatus === 204 ? null : '{"message":"Missing Permissions"}',
				{ status: banStatus },
			),
		});

	const posts = (requests: RecordedRequest[], channel: string) =>
		requests
			.filter((request) => request.path === `/channels/${channel}/messages`)
			.map(
				(request) =>
					request.body as {
						content?: string;
						embeds?: APIEmbed[];
						components?: unknown[];
						message_reference?: unknown;
					},
			);

	it("requires Ban Members", async () => {
		const { body } = await dispatch(
			signer,
			bansSharing("share", [userOption("user", TARGET_ID)], {
				resolved: resolvedTarget,
			}),
		);
		expect(asMessage(body).data.flags).toBe(MessageFlags.Ephemeral);
	});

	it("requires a configured channel", async () => {
		const { body } = await dispatch(signer, share());
		expect(firstEmbed(asMessage(body).data).title).toBe(
			"Не налаштовано канал сповіщень.",
		);
	});

	it("notifies every other server, auto-banning where trusted", async () => {
		await configureNetwork();
		const { body, edited, requests } = await dispatch(
			signer,
			share("spam"),
			network(),
		);
		expect(body.type).toBe(
			InteractionResponseType.DeferredChannelMessageWithSource,
		);

		// Local notice, recording what actually got delivered.
		const [local] = posts(requests, CHANNEL_ID);
		expect(local?.content).toBe(`<@${TARGET_ID}> 'Troll' 'troll'`);
		expect(local?.embeds?.[0]).toMatchObject({
			title: "Новий бан на цьому сервері",
			description: `**Статус:** поширено на 2 з 2 серверів модератором <@${INVOKER_ID}>`,
		});
		expect(local?.embeds?.[0]?.fields).toEqual([
			{ name: "Сервер", value: "Home" },
			{ name: "Модератор", value: "Invoker 'invoker'" },
			{ name: "Забанений", value: `<@${TARGET_ID}> 'Troll' 'troll'` },
			{ name: "guild_id", value: GUILD_ID },
			{ name: "actor_id", value: INVOKER_ID },
			{ name: "target_id", value: TARGET_ID },
			{ name: "reason", value: "spam" },
		]);

		// Untrusting server: buttons plus the copy-pasteable command.
		const [notice, command] = posts(requests, OTHER_CHANNEL);
		expect(notice?.embeds?.[0]?.title).toBe("Новий бан на іншому сервері");
		const row = notice
			?.components?.[0] as APIActionRowComponent<APIComponentInMessageActionRow>;
		expect(
			row.components.map((component) => [
				(component as APIButtonComponentWithCustomId).custom_id,
				(component as APIButtonComponentWithCustomId).disabled,
			]),
		).toEqual([
			[BAN_BUTTON_ID, false],
			[SKIP_BUTTON_ID, false],
		]);
		expect(command).toMatchObject({
			content: `/ban user:${TARGET_ID} delete_messages: reason: spam`,
			message_reference: { message_id: `msg-${OTHER_CHANNEL}` },
		});

		// Trusting server: banned automatically, buttons disabled, no command.
		const ban = requests.find(
			(request) =>
				request.path === `/guilds/${TRUSTING_GUILD}/bans/${TARGET_ID}`,
		);
		expect(ban?.method).toBe("PUT");
		expect(
			decodeURIComponent(ban?.headers.get("x-audit-log-reason") ?? ""),
		).toBe("spam");
		const trusting = posts(requests, TRUSTING_CHANNEL);
		expect(trusting).toHaveLength(1);
		expect(trusting[0]?.embeds?.[0]?.description).toBe(
			`**Статус:** застосовано автоматично, довірений модератор Invoker (${INVOKER_ID})`,
		);

		expect(firstEmbed(edited).description).toBe(
			`Сповіщення про бан <@${TARGET_ID}> відправлено на 2 з 2 серверів.`,
		);
		expect(await db.hasSeenBan(env.DB, TARGET_ID)).toBe(true);
	});

	it("falls back to buttons when the trusted auto-ban is refused", async () => {
		await configureNetwork();
		const { requests } = await dispatch(
			signer,
			share(),
			network({ banStatus: 403 }),
		);
		const trusting = posts(requests, TRUSTING_CHANNEL);
		expect(trusting).toHaveLength(2);
		expect(trusting[0]?.embeds?.[0]?.description).toBeUndefined();
		expect(trusting[1]?.content).toBe(
			`/ban user:${TARGET_ID} delete_messages:`,
		);
	});

	it("refuses to share a ban that does not exist here", async () => {
		await configureNetwork();
		const { edited, requests } = await dispatch(
			signer,
			share(),
			network({ bannedLocally: false }),
		);
		expect(firstEmbed(edited).title).toBe("Користувача не забанено");
		// Nothing was announced anywhere and the ban was not recorded.
		expect(requests.filter((request) => request.method === "POST")).toEqual([]);
		expect(await db.hasSeenBan(env.DB, TARGET_ID)).toBe(false);
	});

	it("refuses to share the same ban twice", async () => {
		await configureNetwork();
		await dispatch(signer, share(), network());
		const { body, requests } = await dispatch(signer, share(), network());
		expect(requests).toEqual([]);
		expect(firstEmbed(asMessage(body).data).title).toBe("Бан вже поширено");
	});

	it("stays shareable when the fan-out fails outright", async () => {
		await configureNetwork();
		const { requests } = await dispatch(
			signer,
			share(),
			discordApi({
				[`GET /guilds/${GUILD_ID}/bans/${TARGET_ID}`]: new Response("{}", {
					status: 200,
				}),
				[`GET /guilds/${GUILD_ID}`]: new Response("{}", { status: 500 }),
			}),
		);
		expect(requests.some((request) => request.method === "POST")).toBe(false);
		// Not marked seen, so the moderator can simply run the command again.
		expect(await db.hasSeenBan(env.DB, TARGET_ID)).toBe(false);
	});

	it("omits buttons where the bot cannot ban", async () => {
		await configureNetwork();
		const { requests } = await dispatch(
			signer,
			share(),
			network({ canBanIn: [] }),
		);

		const [notice, command] = posts(requests, OTHER_CHANNEL);
		expect(notice?.components).toBeUndefined();
		expect(notice?.embeds?.[0]?.footer?.text).toContain(
			"У бота відсутні права на бан",
		);
		expect(command?.content).toBe(`/ban user:${TARGET_ID} delete_messages:`);

		// Trusted moderators do not get an auto-ban there either.
		expect(requests.some((request) => request.method === "PUT")).toBe(false);
		expect(posts(requests, TRUSTING_CHANNEL)).toHaveLength(2);
	});

	it("works from the user context menu too", async () => {
		await configureNetwork();
		const { edited, requests } = await dispatch(
			signer,
			userCommandInteraction("Поширити бан", targetUser, MODERATOR),
			network(),
		);
		expect(posts(requests, OTHER_CHANNEL)[1]?.content).toBe(
			`/ban user:${TARGET_ID} delete_messages:`,
		);
		expect(firstEmbed(edited).title).toBe("Бан поширено");
	});
});

describe("ban notice buttons", () => {
	const notice: APIEmbed = {
		title: "Новий бан на іншому сервері",
		fields: [
			{ name: "Забанений", value: `<@${TARGET_ID}> 'Troll' 'troll'` },
			{ name: "target_id", value: TARGET_ID },
			{ name: "reason", value: "spam" },
		],
	};

	it("bans on click and disables the buttons", async () => {
		const { body, edited, requests } = await dispatch(
			signer,
			buttonInteraction(BAN_BUTTON_ID, [notice], MODERATOR),
			discordApi({
				[`PUT /guilds/${GUILD_ID}/bans/${TARGET_ID}`]: new Response(null, {
					status: 204,
				}),
			}),
		);
		expect(body.type).toBe(InteractionResponseType.DeferredMessageUpdate);
		expect(
			decodeURIComponent(requests[0]?.headers.get("x-audit-log-reason") ?? ""),
		).toBe("spam");
		expect(edited?.embeds?.[0]?.description).toBe(
			`**Статус:** теж забанено модератором <@${INVOKER_ID}>.`,
		);
		const row = edited
			?.components?.[0] as APIActionRowComponent<APIComponentInMessageActionRow>;
		expect(row.components).toMatchObject([
			{ type: ComponentType.Button, style: ButtonStyle.Danger, disabled: true },
			{
				type: ComponentType.Button,
				style: ButtonStyle.Secondary,
				disabled: true,
			},
		]);
	});

	it("bans in the clicked guild, never the one named in the embed", async () => {
		// The embed is just message content; only the interaction is signed.
		const forged: APIEmbed = {
			...notice,
			fields: [
				...(notice.fields ?? []),
				{ name: "guild_id", value: TRUSTING_GUILD },
			],
		};
		const { requests } = await dispatch(
			signer,
			buttonInteraction(BAN_BUTTON_ID, [forged], MODERATOR),
			discordApi({
				[`PUT /guilds/${GUILD_ID}/bans/${TARGET_ID}`]: new Response(null, {
					status: 204,
				}),
			}),
		);
		expect(requests.map((request) => request.path)).toEqual([
			`/guilds/${GUILD_ID}/bans/${TARGET_ID}`,
		]);
	});

	it("reports a refused ban and leaves the buttons live", async () => {
		const { edited } = await dispatch(
			signer,
			buttonInteraction(BAN_BUTTON_ID, [notice], MODERATOR),
			discordApi({
				[`PUT /guilds/${GUILD_ID}/bans/${TARGET_ID}`]: new Response(
					'{"message":"Missing Permissions"}',
					{ status: 403 },
				),
			}),
		);
		expect(edited?.embeds?.[0]?.description).toContain("не вдалося забанити");
		const row = edited
			?.components?.[0] as APIActionRowComponent<APIComponentInMessageActionRow>;
		expect(
			row.components.map(
				(component) => (component as APIButtonComponentWithCustomId).disabled,
			),
		).toEqual([false, false]);
	});

	it("passes no reason through when the notice carries none", async () => {
		const withoutReason: APIEmbed = {
			...notice,
			fields: (notice.fields ?? []).map((field) =>
				field.name === "reason" ? { ...field, value: "​" } : field,
			),
		};
		const { requests } = await dispatch(
			signer,
			buttonInteraction(BAN_BUTTON_ID, [withoutReason], MODERATOR),
			discordApi({
				[`PUT /guilds/${GUILD_ID}/bans/${TARGET_ID}`]: new Response(null, {
					status: 204,
				}),
			}),
		);
		expect(requests[0]?.headers.get("x-audit-log-reason")).toBeNull();
	});

	it("requires Ban Members to click", async () => {
		const { body, requests } = await dispatch(
			signer,
			buttonInteraction(BAN_BUTTON_ID, [notice]),
		);
		expect(requests).toEqual([]);
		expect(asMessage(body).data.flags).toBe(MessageFlags.Ephemeral);
	});

	it("requires Ban Members to skip", async () => {
		const { body } = await dispatch(
			signer,
			buttonInteraction(SKIP_BUTTON_ID, [notice]),
		);
		expect(asMessage(body).data.flags).toBe(MessageFlags.Ephemeral);
	});

	it("marks the notice ignored on skip", async () => {
		const { body, requests } = await dispatch(
			signer,
			buttonInteraction(SKIP_BUTTON_ID, [notice], MODERATOR),
		);
		expect(requests).toEqual([]);
		const update = body as Required<APIInteractionResponseUpdateMessage>;
		expect(update.type).toBe(InteractionResponseType.UpdateMessage);
		expect(update.data.embeds?.[0]?.description).toBe(
			`**Статус:** проігноровано модератором <@${INVOKER_ID}>`,
		);
	});
});
