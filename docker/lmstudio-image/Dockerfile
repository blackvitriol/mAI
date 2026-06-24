ARG UBUNTU_VERSION=22.04
FROM ubuntu:${UBUNTU_VERSION}

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    libatomic1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

ENV LM_STUDIO_HOME=/root/.lmstudio
ENV PATH="/root/.lmstudio/bin:${PATH}"

EXPOSE 1234
ENTRYPOINT ["/entrypoint.sh"]
