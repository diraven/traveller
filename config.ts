require('dotenv').config();

export const DISCORD_BOT_TOKEN = process.env.DISCORD_BOT_TOKEN;
export const DISCORD_APPLICATION_ID = process.env.DISCORD_APPLICATION_ID;
export const DISCORD_PUBLIC_KEY = process.env.DISCORD_PUBLIC_KEY;
export const DISCORD_BOT_GUILD_ID = process.env.DISCORD_BOT_GUILD_ID;
export const DEBUG = process.env.DEBUG;

export const DISCORD_GUILD_IDS = new Map([
  ['diraven', '959896609787887706'],
  ['ruthenia', '739848572526264450'],
  ['the_ukrainians', '996037286267453440'],
  ['ugc', '205691838760353792'],
]);
