# # pull official base image
# FROM python:3.11.1-alpine

# # set work directory
# WORKDIR /usr/src/app
# RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
# # set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
# ENV PATH="${PATH}:/root/.poetry/bin"

# RUN poetry install

# # install dependencies
# # COPY pyproject.toml /usr/src/app
# # RUN apt-get update && apt-get install --no-install-recommends -y curl \
# #     && curl -sSL https://install.python-poetry.org | python

# # RUN pip install --upgrade pip && \
# #     pip install poetry && \
# #     poetry config virtualenvs.create false && \
# #     poetry install --no-interaction --no-ansi


# # copy entrypoint.sh
# COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# # copy project
# COPY . /usr/src/app/

# # run entrypoint.sh
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /project/
# Install dependencies
COPY pyproject.toml /project/
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . /project/

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]