FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.6.1 /uv /uvx /bin/

ENV UV_LINK_MODE=copy

ADD . /app
WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv uv sync

ENV API_BASE=http://host.docker.internal:11434 \
    PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "crewai-agent"]

