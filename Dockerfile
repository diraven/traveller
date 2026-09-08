# Node runs the TypeScript sources directly by stripping types, so there is no
# build step and no compiler in the runtime image.
FROM node:24-alpine

ENV NODE_ENV=production
WORKDIR /app

RUN corepack enable

# Dependencies first, so a source-only change reuses this layer.
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile --prod --ignore-scripts

COPY migrations ./migrations
COPY src ./src

USER node
CMD ["node", "src/index.ts"]
