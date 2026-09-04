import { cloudflareTest, readD1Migrations } from "@cloudflare/vitest-plugin";
import { defineConfig } from "vitest/config";

export default defineConfig(async () => {
  // Handed to the test worker as a binding and applied by test/setup.ts.
  const migrations = await readD1Migrations("migrations");

  return {
    plugins: [
      cloudflareTest({
        wrangler: { configPath: "./wrangler.jsonc" },
        miniflare: { bindings: { TEST_MIGRATIONS: migrations } },
      }),
    ],
    test: {
      setupFiles: ["./test/setup.ts"],
      deps: {
        optimizer: {
          ssr: {
            // CommonJS packages need pre-bundling to run inside workerd.
            enabled: true,
            include: ["discord-api-types/v10"],
          },
        },
      },
    },
  };
});
