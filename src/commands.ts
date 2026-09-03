/**
 * Command definitions shared by the runtime router and the registration
 * script, so the two can never drift apart.
 */
import {
  ApplicationCommandOptionType,
  ApplicationCommandType,
  ApplicationIntegrationType,
  InteractionContextType,
  type RESTPostAPIChatInputApplicationCommandsJSONBody,
} from "discord-api-types/v10";

import { FAQ_ENTRIES } from "./faq_entries.ts";

/** Every command is installed on servers only and usable inside servers only. */
const GUILD_ONLY: Pick<
  RESTPostAPIChatInputApplicationCommandsJSONBody,
  "type" | "integration_types" | "contexts"
> = {
  type: ApplicationCommandType.ChatInput,
  integration_types: [ApplicationIntegrationType.GuildInstall],
  contexts: [InteractionContextType.Guild],
};

export const FAQ_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody = {
  ...GUILD_ONLY,
  name: "faq",
  description: "ЧаПи",
  options: Object.entries(FAQ_ENTRIES).map(([name, entry]) => ({
    type: ApplicationCommandOptionType.Subcommand,
    name,
    description: entry.title,
  })),
};

export const SLAP_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody = {
  ...GUILD_ONLY,
  name: "slap",
  description: "Йой!",
  options: [
    {
      type: ApplicationCommandOptionType.User,
      name: "member",
      description: "Кого",
      required: true,
    },
  ],
};

export const SUM_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody = {
  ...GUILD_ONLY,
  name: "sum",
  description: "Словник української мови (sum.in.ua)",
  options: [
    {
      type: ApplicationCommandOptionType.String,
      name: "word",
      description: "Слово",
      required: true,
    },
  ],
};

export const SUM20_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody = {
  ...GUILD_ONLY,
  name: "sum20",
  description: "Словник української мови (sum20ua.com)",
  options: [
    {
      type: ApplicationCommandOptionType.String,
      name: "word",
      description: "Слово",
      required: true,
    },
  ],
};

export const RUSNI_PYZDA_COMMAND: RESTPostAPIChatInputApplicationCommandsJSONBody =
  {
    ...GUILD_ONLY,
    name: "rusni_pyzda",
    description: "Втрати РФ станом на сьогодні.",
  };

export const COMMANDS: RESTPostAPIChatInputApplicationCommandsJSONBody[] = [
  FAQ_COMMAND,
  SLAP_COMMAND,
  SUM_COMMAND,
  SUM20_COMMAND,
  RUSNI_PYZDA_COMMAND,
];
