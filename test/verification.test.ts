import { env } from "cloudflare:test";
import {
  InteractionResponseType,
  MessageFlags,
  PermissionFlagsBits,
  type APIInteractionResponseChannelMessageWithSource,
} from "discord-api-types/v10";
import { beforeAll, describe, expect, it } from "vitest";

import * as db from "../src/db.ts";
import { Color } from "../src/discord.ts";
import { discordApi, dispatch, firstEmbed } from "./harness.ts";
import {
  APPLICATION_ID,
  GUILD_ID,
  INVOKER_ID,
  ROLE_ID,
  TARGET_ID,
  chatInputInteraction,
  createSigner,
  resolvedMember,
  roleOption,
  subcommand,
  user,
  userOption,
  type Signer,
} from "./helpers.ts";

let signer: Signer;

beforeAll(async () => {
  signer = await createSigner();
});

const ADMIN = { permissions: PermissionFlagsBits.Administrator };

function asMessage(body: unknown) {
  return body as APIInteractionResponseChannelMessageWithSource;
}

describe("/verification set_role", () => {
  it("refuses non-administrators", async () => {
    const { body } = await dispatch(
      signer,
      chatInputInteraction("verification", [
        subcommand("set_role", [roleOption("role", ROLE_ID)]),
      ]),
    );
    expect(asMessage(body).data.flags).toBe(MessageFlags.Ephemeral);
    expect(firstEmbed(asMessage(body).data).description).toBe(
      "Відсутній доступ.",
    );
  });

  it("stores the role for the guild", async () => {
    const { body } = await dispatch(
      signer,
      chatInputInteraction(
        "verification",
        [subcommand("set_role", [roleOption("role", ROLE_ID)])],
        ADMIN,
      ),
    );
    expect(firstEmbed(asMessage(body).data).description).toBe(
      `Нова роль верифікації: <@&${ROLE_ID}>`,
    );
    expect(await db.getGuild(env.DB, GUILD_ID)).toMatchObject({
      verification_role_id: ROLE_ID,
      bans_sharing_channel_id: null,
    });
  });
});

describe("/verification check_config", () => {
  const checkConfig = () =>
    chatInputInteraction("verification", [subcommand("check_config")], ADMIN);

  const guildRoles = (
    verificationPosition: number,
    botPosition: number,
    manageRoles = true,
  ) =>
    discordApi({
      "GET /users/@me/guilds?limit=200": [
        {
          id: GUILD_ID,
          permissions: (manageRoles
            ? PermissionFlagsBits.ManageRoles
            : PermissionFlagsBits.SendMessages
          ).toString(),
        },
      ],
      [`GET /guilds/${GUILD_ID}/roles`]: [
        { id: GUILD_ID, name: "@everyone", position: 0 },
        { id: ROLE_ID, name: "Verified", position: verificationPosition },
        { id: "bot-role", name: "Traveller", position: botPosition },
      ],
      [`GET /guilds/${GUILD_ID}/members/${APPLICATION_ID}`]: {
        roles: ["bot-role"],
      },
    });

  it("passes when the role sits below the bot's role", async () => {
    await db.setVerificationRole(env.DB, GUILD_ID, ROLE_ID);
    const { body, edited } = await dispatch(
      signer,
      checkConfig(),
      guildRoles(1, 2),
    );
    expect(body.type).toBe(
      InteractionResponseType.DeferredChannelMessageWithSource,
    );
    const embed = firstEmbed(edited);
    expect(embed.description).toBe("Все ок.");
    expect(embed.color).toBe(Color.green);
    expect(embed.fields).toEqual([]);
  });

  it("reports a missing role setting without inspecting roles", async () => {
    const { edited, requests } = await dispatch(
      signer,
      checkConfig(),
      guildRoles(1, 2),
    );
    expect(requests.map((request) => request.path)).toEqual([
      "/users/@me/guilds?limit=200",
    ]);
    const embed = firstEmbed(edited);
    expect(embed.color).toBe(Color.red);
    expect(embed.fields).toMatchObject([
      { name: "Роль верифікації не задана." },
    ]);
  });

  it("reports a role above the bot and missing Manage Roles", async () => {
    await db.setVerificationRole(env.DB, GUILD_ID, ROLE_ID);
    const { edited } = await dispatch(
      signer,
      checkConfig(),
      guildRoles(3, 2, false),
    );
    expect(firstEmbed(edited).fields?.map((field) => field.name)).toEqual([
      "Відсутній дозвіл на управління ролями.",
      `Відсутній дозвіл для видачі ролі <@&${ROLE_ID}>.`,
    ]);
  });

  it("reports a deleted role", async () => {
    await db.setVerificationRole(env.DB, GUILD_ID, "gone");
    const { edited } = await dispatch(signer, checkConfig(), guildRoles(1, 2));
    expect(firstEmbed(edited).fields).toMatchObject([
      { name: "Роль верифікації не знайдено." },
    ]);
  });
});

describe("/verify", () => {
  const verify = (
    targetId: string,
    { actorRoles = [ROLE_ID], targetRoles = [] as string[] } = {},
  ) =>
    chatInputInteraction("verify", [userOption("member", targetId)], {
      roles: actorRoles,
      resolved: {
        users: { [targetId]: user(targetId) },
        members: { [targetId]: resolvedMember(targetRoles) },
      },
    });

  const addRole = `PUT /guilds/${GUILD_ID}/members/${TARGET_ID}/roles/${ROLE_ID}`;

  it("assigns the role and credits the verifier in the audit log", async () => {
    await db.setVerificationRole(env.DB, GUILD_ID, ROLE_ID);
    const { edited, requests } = await dispatch(
      signer,
      verify(TARGET_ID),
      discordApi({ [addRole]: new Response(null, { status: 204 }) }),
    );

    expect(requests).toHaveLength(1);
    expect(requests[0]?.headers.get("authorization")).toBe("Bot bot-token");
    expect(
      decodeURIComponent(requests[0]?.headers.get("x-audit-log-reason") ?? ""),
    ).toBe(`<@${INVOKER_ID}> 'invoker' (${INVOKER_ID})`);
    const embed = firstEmbed(edited);
    expect(embed.title).toBe("Верифікація");
    expect(embed.description).toContain(
      `<@${INVOKER_ID}> верифікує <@${TARGET_ID}>`,
    );
    expect(embed.color).toBe(Color.green);
  });

  it("refuses self-verification", async () => {
    const { body, requests } = await dispatch(signer, verify(INVOKER_ID));
    expect(requests).toEqual([]);
    expect(firstEmbed(asMessage(body).data).title).toBe("???");
  });

  it("refuses to verify the bot", async () => {
    const { body } = await dispatch(signer, verify(APPLICATION_ID));
    expect(firstEmbed(asMessage(body).data).description).toBe("А мене за шо?)");
  });

  it("points administrators to check_config when unconfigured", async () => {
    const { body } = await dispatch(signer, verify(TARGET_ID));
    expect(firstEmbed(asMessage(body).data).description).toContain(
      "/verification check_config",
    );
  });

  it("requires the verifier to be verified", async () => {
    await db.setVerificationRole(env.DB, GUILD_ID, ROLE_ID);
    const { body } = await dispatch(
      signer,
      verify(TARGET_ID, { actorRoles: [] }),
    );
    expect(firstEmbed(asMessage(body).data).description).toBe(
      "Тільки верифіковані користувачі можуть верифікувати інших.",
    );
  });

  it("rejects already verified targets", async () => {
    await db.setVerificationRole(env.DB, GUILD_ID, ROLE_ID);
    const { body } = await dispatch(
      signer,
      verify(TARGET_ID, { targetRoles: [ROLE_ID] }),
    );
    expect(firstEmbed(asMessage(body).data).description).toBe(
      `Користувача <@${TARGET_ID}> вже верифіковано.`,
    );
  });

  it("explains a Discord refusal instead of crashing", async () => {
    await db.setVerificationRole(env.DB, GUILD_ID, ROLE_ID);
    const { edited } = await dispatch(
      signer,
      verify(TARGET_ID),
      discordApi({
        [addRole]: new Response('{"message":"Missing Permissions"}', {
          status: 403,
        }),
      }),
    );
    const embed = firstEmbed(edited);
    expect(embed.title).toBe("Помилка");
    expect(embed.description).toContain("/verification check_config");
  });
});
