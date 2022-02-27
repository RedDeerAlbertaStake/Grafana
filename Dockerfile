FROM python:3.10.2-slim AS base

ENV PIP_NO_CACHE_DIR=off \
    PYTHONDONTWRITEBYTECODE=1

RUN apt update && apt install -y curl wget unzip gnupg software-properties-common

RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb

RUN wget -q https://chromedriver.storage.googleapis.com/98.0.4758.102/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin && \
    chmod 755 /usr/local/bin/chromedriver && \
    rm -f chromedriver_linux64.zip

RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add - && \
    apt-add-repository "deb [arch=$(dpkg --print-architecture)] https://apt.releases.hashicorp.com $(lsb_release -cs) main" && \
    apt update && \
    apt install -y terraform

FROM base as poetry

RUN python -m pip install poetry~=1.1


FROM poetry AS build

COPY pyproject.toml poetry.lock /

RUN python -m venv .venv
RUN poetry install --no-root --no-dev

COPY tm_data/run.py /app/run.py


FROM base AS final

COPY --from=build .venv .venv
COPY --from=build app app

VOLUME /app/terraform
WORKDIR /app

RUN apt full-upgrade -y

USER 1000

CMD [ "/.venv/bin/python", "-u", "/app/run.py" ]
