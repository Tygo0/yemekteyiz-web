# Multi-stage: build the SPA with Node, then serve the static output with
# nginx — no Node runtime needed in the final image.
FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY . .

# Same reasoning as backend/build_executable.py's frontend build step: a
# relative /api base URL lets nginx reverse-proxy same-origin, so the
# browser never needs to know the backend container's address and there's
# no CORS configuration to get right.
RUN echo "VITE_API_BASE_URL=/api" > .env.production && npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
