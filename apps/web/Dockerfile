FROM node:20-alpine

WORKDIR /app

# Copy workspace manifests and package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages/database/package.json ./packages/database/package.json

# Install pnpm
RUN npm install -g pnpm

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Expose Next.js dev port
EXPOSE 3000

# Run dev server
CMD ["pnpm", "--filter", "@evijnar/web", "dev"]
