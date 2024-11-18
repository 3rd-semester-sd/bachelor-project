# Step 1: Use a lightweight Node.js base image
FROM node:18-alpine AS base

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json for installing dependencies
COPY package.json pnpm-lock.yaml* ./

# Install pnpm
RUN npm install -g pnpm

# Install production dependencies
RUN pnpm install --frozen-lockfile --prod

# Step 2: Build Stage
FROM base AS build

# Install build dependencies
RUN pnpm install --frozen-lockfile

# Copy the source code
COPY . .

# Build the app
RUN pnpm build

# Step 3: Production Stage
FROM node:18-alpine AS production

# Set the working directory
WORKDIR /app

# Copy the production dependencies from the base stage
COPY --from=base /app/node_modules ./node_modules

# Copy the built app from the build stage
COPY --from=build /app/dist ./dist

# Copy additional required static assets
COPY --from=build /app/dist/static ./static

# Expose the application's port
EXPOSE 3000

# Define the command to run the application
CMD ["node", "dist/main.js"]
