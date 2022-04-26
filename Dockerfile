FROM node:18

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn

COPY . .
RUN npx tsc

CMD ["node", "index.js"]
