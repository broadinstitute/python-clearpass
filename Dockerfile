FROM python:3.8-slim

COPY poetry.lock pyproject.toml README.md /usr/src/
RUN apt-get update \
    && apt-get upgrade -yq \
    && apt-get install -yq curl g++ gcc git \
    && cd /usr/src \
    && pip install pip poetry --upgrade \
    && if [ ! -s poetry.lock ]; then rm -f poetry.lock; fi \
    && poetry install \
    && rm -rf /tmp/* \
    && rm -rf /var/cache/apt/* \
    && rm -rf /var/tmp/*

WORKDIR /usr/src

ENTRYPOINT ["poetry", "run"]
CMD ["bash"]
