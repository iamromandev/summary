### base image ###
ARG PYTHON_VERSION=3.12.10

FROM python:$PYTHON_VERSION AS base

## arguements ##
ARG ENV
ARG WORK_DIR
ARG INSTALL_DIR
ARG PW_DIR

## environments ##
ENV ENV=$ENV
ENV WORK_DIR=$WORK_DIR
ENV INSTALL_DIR=$INSTALL_DIR
ENV PW_DIR=$PW_DIR
# python
ENV PYTHONUNBUFFERED=true
ENV PYTHONFAULTHANDLER=true
ENV PYTHONDONTWRITEBYTECODE=true
ENV PYTHONHASHSEED=random
# path
ENV VENV_PATH="$INSTALL_DIR/.venv"

# prepend venv to path
ENV PATH="$VENV_PATH/bin:$PATH"

### builder image ###
FROM base AS builder

ARG ENV
ARG WORK_DIR
ARG INSTALL_DIR
ARG PW_DIR

ENV ENV=$ENV
ENV WORK_DIR=$WORK_DIR
ENV INSTALL_DIR=$INSTALL_DIR
ENV PW_DIR=$PW_DIR


# install uv
RUN pip install --upgrade pip
RUN pip install uv

# copy project requirement files here to ensure they will be cached.
WORKDIR $INSTALL_DIR
COPY pyproject.toml $INSTALL_DIR

# create and activate virtual environment
RUN uv venv

# install runtime deps
RUN uv pip install -r $INSTALL_DIR/pyproject.toml
#RUN playwright install --with-deps chromium


### local image ###
FROM base AS local

ARG ENV
ARG WORK_DIR
ARG INSTALL_DIR
ARG PW_DIR

ENV ENV=$ENV
ENV WORK_DIR=$WORK_DIR
ENV INSTALL_DIR=$INSTALL_DIR
ENV PW_DIR=$PW_DIR

WORKDIR $WORK_DIR

COPY --from=builder $INSTALL_DIR $INSTALL_DIR
#COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright
COPY . $WORK_DIR
RUN playwright install --with-deps chromium