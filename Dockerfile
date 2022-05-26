# used this example as a reference: https://github.com/python-poetry/poetry/discussions/1879#discussioncomment-216865
# `python-base` sets up all our shared environment variables
FROM python:3.10.1-slim as python-base

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
    POETRY_HOME="/opt/poetry" \
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


# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base as builder-base
RUN apt update \
    && apt install --no-install-recommends -y \
        curl \
        # deps for building python deps
        git \
        build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
# workaround for "ModuleNotFoundError: No module named 'cleo'" on py3.9
RUN ln -s $POETRY_HOME/lib/poetry/_vendor/py3.8 $POETRY_HOME/lib/poetry/_vendor/py3.9

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev


# `development` image is used during development / testing
FROM python-base as development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH


# quicker install as runtime deps are already installed
RUN poetry install

# will become mountpoint of our code
COPY . /app/
WORKDIR /app


FROM python-base as runtime
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ./jpoetry /app/jpoetry/
COPY ./resources /app/resources/
WORKDIR /app

CMD ["python", "-m", "jpoetry"]