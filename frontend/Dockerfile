FROM node:18-alpine

WORKDIR /app

COPY . /app

RUN npm install
RUN npm run build

CMD ["npx", "serve", "-s", "build", "-l", "3000"]
