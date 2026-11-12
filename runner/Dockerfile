FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ENV PLAYWRIGHT_BROWSERS_PATH=/home/runner/pw-browsers

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git jq sudo python3 python3-venv python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash runner \
    && echo "runner ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/runner

USER runner
WORKDIR /home/runner/actions-runner

# Latest official GitHub Actions runner (linux x64) and its OS dependencies.
RUN VERSION=$(curl -fsSL https://api.github.com/repos/actions/runner/releases/latest | jq -r .tag_name | tr -d v) \
    && curl -fsSL "https://github.com/actions/runner/releases/download/v${VERSION}/actions-runner-linux-x64-${VERSION}.tar.gz" | tar xz

USER root
RUN ./bin/installdependencies.sh && rm -rf /var/lib/apt/lists/*
USER runner

COPY --chown=runner:runner entrypoint.sh /home/runner/entrypoint.sh
RUN chmod +x /home/runner/entrypoint.sh
ENTRYPOINT ["/home/runner/entrypoint.sh"]
