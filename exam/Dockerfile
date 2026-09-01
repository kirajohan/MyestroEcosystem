# ═══════════════════════════════════════════════════════════
# Stage 1: Dependencies
# ═══════════════════════════════════════════════════════════
FROM node:20-alpine AS deps

WORKDIR /app

# curl healthcheck uchun kerak
RUN apk add --no-cache curl

COPY package.json package-lock.json* ./
RUN npm install

# ═══════════════════════════════════════════════════════════
# Stage 2: Build
# ═══════════════════════════════════════════════════════════
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build argumentlar
ARG NEXT_PUBLIC_API_URL=http://localhost:8002
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# ═══════════════════════════════════════════════════════════
# Stage 3: Production
# ═══════════════════════════════════════════════════════════
FROM node:20-alpine AS runner

WORKDIR /app

# curl healthcheck uchun
RUN apk add --no-cache curl

ENV NODE_ENV=production

# Xavfsizlik: non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY package.json ./

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]