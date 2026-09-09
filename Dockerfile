# Node runs the TypeScript sources directly by stripping types, so there is no
# build step and no compiler in the runtime image. The major matches .nvmrc, so
# production runs what CI and development test against.
FROM node:26-alpine

ENV NODE_ENV=production
WORKDIR /app

# Node 25 dropped the bundled corepack, so it is installed rather than enabled.
# It reads the pnpm version from package.json's packageManager field.
RUN npm install --global corepack@latest && corepack enable

# Dependencies first, so a source-only change reuses this layer.
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile --prod --ignore-scripts

COPY migrations ./migrations
COPY src ./src

USER node
CMD ["node", "src/index.ts"]
