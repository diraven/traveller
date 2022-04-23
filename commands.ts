import * as ping from "./commands/ping";
import * as server from "./commands/server";
import * as user from "./commands/user";
import { Command } from "./types/command";

export var commands = [ping, server, user].map((module) => module.cmd);

export function find_command(name: string): Command {
  return commands.find((cmd) => cmd.data.name == name);
}
