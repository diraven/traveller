import { cloudflareTest } from "@cloudflare/vitest-plugin";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [cloudflareTest({ wrangler: { configPath: "./wrangler.jsonc" } })],
  test: {
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
});
