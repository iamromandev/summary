### base image ###
ARG PYTHON_VERSION=3.13.2

FROM python:$PYTHON_VERSION AS base

## arguements ##
# env
ARG ENV
# workdir
ARG WORK_DIR
# path
ARG SETUP_PATH="/opt/setup"

## environments ##
# env
ENV ENV=$ENV
# workdir
ENV WORK_DIR=$WORK_DIR
# python
ENV PYTHONUNBUFFERED=true
ENV PYTHONFAULTHANDLER=true
ENV PYTHONDONTWRITEBYTECODE=true
ENV PYTHONHASHSEED=random
# path
ENV SETUP_PATH=$SETUP_PATH
ENV VENV_PATH="$SETUP_PATH/.venv"

# prepend venv to path
ENV PATH="$VENV_PATH/bin:$PATH"

### builder image ###
FROM base AS builder

ARG ENV
ARG WORK_DIR

ENV ENV=$ENV
ENV WORK_DIR=$WORK_DIR

# install uv
RUN pip install --upgrade pip
RUN pip install uv

# copy project requirement files here to ensure they will be cached.
WORKDIR $SETUP_PATH
COPY pyproject.toml $SETUP_PATH

# Create and activate virtual environment
RUN uv venv

# install runtime deps
RUN uv pip install -r $SETUP_PATH/pyproject.toml

### local image ###
FROM base AS local

ARG ENV
ARG WORK_DIR

ENV ENV=$ENV
ENV WORK_DIR=$WORK_DIR

WORKDIR $WORK_DIR

COPY --from=builder $SETUP_PATH $SETUP_PATH
COPY . $WORK_DIR
RUN playwright install --with-deps chromium firefox webkit