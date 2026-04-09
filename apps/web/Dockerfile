# apps/web/Dockerfile.dev
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install pnpm
RUN npm install -g pnpm

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Expose Next.js dev port
EXPOSE 3000

# Run dev server
CMD ["pnpm", "dev"]
