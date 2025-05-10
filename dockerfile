### base image ###
ARG PYTHON_VERSION=3.13.2

FROM python:$PYTHON_VERSION AS base

## arguements ##
ARG ENV
ARG WORK_DIR
ARG PW_DIR
ARG SETUP_PATH="/opt/setup"

## environments ##
ENV ENV=$ENV
ENV WORK_DIR=$WORK_DIR
ENV PW_DIR=$PW_DIR
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
ARG PW_DIR

ENV ENV=$ENV
ENV WORK_DIR=$WORK_DIR
ENV PW_DIR=$PW_DIR

# install uv
RUN pip install --upgrade pip
RUN pip install uv

# copy project requirement files here to ensure they will be cached.
WORKDIR $SETUP_PATH
COPY pyproject.toml $SETUP_PATH

# create and activate virtual environment
RUN uv venv

# install runtime deps
RUN uv pip install -r $SETUP_PATH/pyproject.toml


### local image ###
FROM base AS local

ARG ENV
ARG WORK_DIR
ARG PW_DIR

ENV ENV=$ENV
ENV WORK_DIR=$WORK_DIR
ENV PW_DIR=$PW_DIR

# set environment variables for playwright to find browsers
ENV PLAYWRIGHT_BROWSERS_PATH=$PW_DIR

WORKDIR $WORK_DIR

COPY --from=builder $SETUP_PATH $SETUP_PATH
COPY . $WORK_DIR
RUN playwright install --with-deps chromium