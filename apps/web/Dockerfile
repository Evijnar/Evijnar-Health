FROM node:20-alpine

WORKDIR /app

# Copy package manifest
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose Next.js dev port
EXPOSE 3000

# Run dev server
CMD ["npm", "run", "dev"]
