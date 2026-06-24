ARG OPENCLAW_VERSION=2026.5.4
FROM ghcr.io/openclaw/openclaw:${OPENCLAW_VERSION}

USER root

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
