ARG NODE_IMAGE=node:22-bookworm-slim
FROM ${NODE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive

# Runtime libraries required by Puppeteer-downloaded Chrome (glibc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    tini \
    wget \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

ARG N8N_VERSION=2.26.6
RUN npm install -g "n8n@${N8N_VERSION}"

COPY entrypoint.sh /entrypoint.sh
COPY setup-deps.sh /setup-deps.sh
RUN sed -i 's/\r$//' /entrypoint.sh /setup-deps.sh && chmod +x /entrypoint.sh /setup-deps.sh

USER node
WORKDIR /home/node

ENV PUPPETEER_CACHE_DIR=/home/node/.n8n/puppeteer-cache

EXPOSE 5678
ENTRYPOINT ["tini", "--", "/entrypoint.sh"]
CMD ["start"]
