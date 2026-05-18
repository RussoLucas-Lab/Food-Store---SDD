FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --legacy-peer-deps
COPY . .
ARG VITE_API_URL=http://localhost:8000
ARG VITE_MP_PUBLIC_KEY=TEST-key
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_MP_PUBLIC_KEY=$VITE_MP_PUBLIC_KEY
RUN npm run build

FROM nginx:alpine AS runner
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
