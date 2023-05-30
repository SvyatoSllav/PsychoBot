FROM python:3.10-slim-buster

WORKDIR /project/

RUN pip install --no-cache-dir poetry

COPY ./pyproject.toml ./poetry.lock /project/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev --verbose
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY . /project/

COPY ./entrypoint.sh /usr/src/project/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/usr/src/project/entrypoint.sh"]