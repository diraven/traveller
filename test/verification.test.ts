import { PermissionFlagsBits } from "discord.js";
import { describe, expect, it } from "vitest";

import { Color } from "../src/discord.ts";
import { verification, verify } from "../src/handlers/verification.ts";
import {
	asCommand,
	fakeDb,
	fakeGuild,
	fakeInteraction,
	fakeMember,
	fakeUser,
	firstEmbed,
} from "./fakes.ts";

const ROLE_ID = "role1";

/** getGuild's row, with verification configured unless told otherwise. */
function configured(roleId: string | null = ROLE_ID) {
	return fakeDb([
		{
			match: "AS id",
			rows: [
				{
					id: "guild1",
					bans_sharing_channel_id: null,
					verification_role_id: roleId,
				},
			],
		},
	]);
}

describe("verify", () => {
	it("refuses self-verification", async () => {
		const actor = fakeUser({ id: "1" });
		const interaction = fakeInteraction({
			user: actor,
			users: { member: actor },
		});
		await verify(asCommand(interaction), { db: configured() });

		expect(firstEmbed(interaction.reply)?.title).toBe("???");
		expect(interaction.deferReply).not.toHaveBeenCalled();
	});

	it("refuses to verify the bot", async () => {
		const interaction = fakeInteraction({
			user: fakeUser({ id: "1" }),
			users: { member: fakeUser({ id: "bot" }) },
		});
		await verify(asCommand(interaction), { db: configured() });

		expect(firstEmbed(interaction.reply)?.description).toBe("А мене за шо?)");
	});

	it("points at check_config when no role is set", async () => {
		const interaction = fakeInteraction({
			user: fakeUser({ id: "1" }),
			users: { member: fakeUser({ id: "2" }) },
		});
		await verify(asCommand(interaction), { db: configured(null) });

		expect(firstEmbed(interaction.reply)?.description).toContain(
			"/verification check_config",
		);
	});

	it("only lets verified members verify others", async () => {
		const interaction = fakeInteraction({
			user: fakeUser({ id: "1" }),
			users: { member: fakeUser({ id: "2" }) },
			memberRoles: [],
		});
		await verify(asCommand(interaction), { db: configured() });

		expect(firstEmbed(interaction.reply)?.description).toContain(
			"Тільки верифіковані",
		);
	});

	it("reports a member who already has the role", async () => {
		const interaction = fakeInteraction({
			user: fakeUser({ id: "1" }),
			users: { member: fakeUser({ id: "2" }) },
			memberRoles: [ROLE_ID],
			members: { member: fakeMember([ROLE_ID]) },
		});
		await verify(asCommand(interaction), { db: configured() });

		expect(firstEmbed(interaction.reply)?.description).toContain(
			"вже верифіковано",
		);
	});

	it("grants the role deferred, naming the moderator in the audit log", async () => {
		const member = fakeMember([]);
		const interaction = fakeInteraction({
			user: fakeUser({ id: "1", username: "mod" }),
			users: { member: fakeUser({ id: "2" }) },
			memberRoles: [ROLE_ID],
			members: { member },
		});
		await verify(asCommand(interaction), { db: configured() });

		expect(interaction.deferReply).toHaveBeenCalled();
		expect(member.roles.add).toHaveBeenCalledWith(
			ROLE_ID,
			expect.stringContaining("'mod' (1)"),
		);
		expect(firstEmbed(interaction.editReply)?.color).toBe(Color.green);
	});
});

describe("verification set_role", () => {
	it("refuses non-administrators", async () => {
		const interaction = fakeInteraction({
			subcommand: "set_role",
			permissions: [],
		});
		const db = configured();
		await verification(asCommand(interaction), { db });

		expect(firstEmbed(interaction.reply)?.description).toBe(
			"Відсутній доступ.",
		);
		expect(db.queries).toHaveLength(0);
	});

	it("stores the role", async () => {
		const interaction = fakeInteraction({
			subcommand: "set_role",
			permissions: [PermissionFlagsBits.Administrator],
			roles: { role: { id: ROLE_ID } },
		});
		const db = configured();
		await verification(asCommand(interaction), { db });

		expect(db.queries[0]?.sql).toContain("verification_role_id");
		expect(db.queries[0]?.values).toEqual(["guild1", ROLE_ID]);
	});
});

describe("verification check_config", () => {
	it("reports a missing Manage Roles permission", async () => {
		const interaction = fakeInteraction({
			subcommand: "check_config",
			permissions: [PermissionFlagsBits.Administrator],
			guild: fakeGuild({ mePermissions: [] }),
		});
		await verification(asCommand(interaction), { db: configured(null) });

		const embed = firstEmbed(interaction.editReply) as {
			fields: { name: string }[];
			color: number;
		};
		expect(embed.color).toBe(Color.red);
		expect(embed.fields.map((field) => field.name)).toContain(
			"Відсутній дозвіл на управління ролями.",
		);
	});

	it("reports a verification role the bot cannot hand out", async () => {
		const interaction = fakeInteraction({
			subcommand: "check_config",
			permissions: [PermissionFlagsBits.Administrator],
			guild: fakeGuild({
				mePermissions: [PermissionFlagsBits.ManageRoles],
				meTopRole: 5,
				roles: [{ id: ROLE_ID, position: 9 }],
			}),
		});
		await verification(asCommand(interaction), { db: configured() });

		const embed = firstEmbed(interaction.editReply) as {
			fields: { name: string }[];
		};
		expect(embed.fields[0]?.name).toContain("Відсутній дозвіл для видачі ролі");
	});

	it("says all is well when the role sits below the bot", async () => {
		const interaction = fakeInteraction({
			subcommand: "check_config",
			permissions: [PermissionFlagsBits.Administrator],
			guild: fakeGuild({
				mePermissions: [PermissionFlagsBits.ManageRoles],
				meTopRole: 10,
				roles: [{ id: ROLE_ID, position: 3 }],
			}),
		});
		await verification(asCommand(interaction), { db: configured() });

		expect(firstEmbed(interaction.editReply)?.description).toBe("Все ок.");
	});
});
