/**
 * A minimal forward-only migration runner: every `.sql` file in `migrations/`
 * is applied once, in filename order, inside a transaction, and recorded in
 * `schema_migrations`.
 *
 * The bot runs this at startup, so a deploy never needs a separate step. It can
 * also be run on its own with `pnpm db:migrate`.
 */
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import type { Pool } from "pg";

const MIGRATIONS_DIR = "migrations";

export async function migrate(pool: Pool): Promise<string[]> {
	await pool.query(
		`CREATE TABLE IF NOT EXISTS schema_migrations (
       name text PRIMARY KEY,
       applied_at timestamptz NOT NULL DEFAULT now()
     )`,
	);

	const { rows } = await pool.query<{ name: string }>(
		"SELECT name FROM schema_migrations",
	);
	const applied = new Set(rows.map((row) => row.name));

	const files = (await readdir(MIGRATIONS_DIR))
		.filter((file) => file.endsWith(".sql"))
		.sort();

	const ran: string[] = [];
	for (const file of files) {
		if (applied.has(file)) {
			continue;
		}
		const sql = await readFile(path.join(MIGRATIONS_DIR, file), "utf8");
		const client = await pool.connect();
		try {
			await client.query("BEGIN");
			await client.query(sql);
			await client.query("INSERT INTO schema_migrations (name) VALUES ($1)", [
				file,
			]);
			await client.query("COMMIT");
		} catch (error) {
			await client.query("ROLLBACK");
			throw new Error(`Migration ${file} failed: ${String(error)}`, {
				cause: error,
			});
		} finally {
			client.release();
		}
		ran.push(file);
	}
	return ran;
}

if (process.argv[1] && import.meta.filename === path.resolve(process.argv[1])) {
	const { Pool } = await import("pg");
	const { config } = await import("./config.ts");
	const pool = new Pool({ connectionString: config.databaseUrl });
	try {
		const ran = await migrate(pool);
		console.log(
			ran.length ? `Applied: ${ran.join(", ")}` : "Nothing to apply.",
		);
	} finally {
		await pool.end();
	}
}
