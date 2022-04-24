import * as ping from "./commands/ping";
import * as server from "./commands/server";
import * as user from "./commands/user";
import * as games from "./commands/games";
import { Command } from "./types/command";

export const commands = [ping, server, user, games].map((module) => module.cmd);

export function find_command(name: string): Command {
  return commands.find((cmd) => cmd.data.name == name);
}
