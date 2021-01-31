# Crabot

Is a discord bot that helps with the discord server public roles management.

## Usage

### Development
- Use vscode, open project and follow prompts.

or

- Create `docker-compose`, see `.devcontainer/docker-compose.yml` for reference.
- Create `.env`, see `example.env` for reference.
- `docker-compose up`.

### Deployment
- `docker pull ghcr.io/diraven/crabot:master`.
- Create `docker-compose`, see `docker-compose.prod.yml` for reference.
- Create `.env`, see `example.env` for reference.
- `docker-compose up -d`.
- Invite your bot to the guild.
- Type `.ping` to verify if it works.
