# used this example as a reference: https://github.com/python-poetry/poetry/discussions/1879#discussioncomment-216865
# `python-base` sets up all our shared environment variables
# there are issues when running on arm64 (dawg related)
ARG TARGETPLATFORM=linux/amd64
FROM --platform=${TARGETPLATFORM} python:3.10.1-slim AS python-base

    # python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.0.3 \
    # make poetry install to this location (commented since doesn't work when installing via pip)
    PIPX_HOME="/opt/pipx" \
    PIPX_BIN_DIR="/usr/local/bin" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"


# prepend venv to path
ENV PATH="$VENV_PATH/bin:$PATH"


# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base AS builder-base
RUN apt update \
    && apt install --no-install-recommends -y \
        curl \
        # deps for building python deps
        git \
        build-essential

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv uv sync


# `development` image is used during development / testing
FROM python-base AS development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $PIPX_HOME $PIPX_HOME
COPY --from=builder-base $PIPX_BIN_DIR $PIPX_BIN_DIR
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH


# quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache poetry install

# will become mountpoint of our code
COPY . /app/
WORKDIR /app


FROM python-base AS runtime
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ./jpoetry /app/jpoetry/
COPY ./resources /app/resources/
WORKDIR /app

CMD ["python", "-m", "jpoetry"]