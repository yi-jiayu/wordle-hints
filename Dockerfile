FROM python:3.10-slim-buster

RUN apt-get update -y && apt-get upgrade -y

WORKDIR /app
COPY ["Pipfile", "Pipfile.lock", "./"]
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile

# Build cache, WORDLE_FOLDER determines where the wordle cache is stored. Path will be /app/.wordle
ENV WORDLE_FOLDER=/app
COPY ["data_source.py", "./"]
RUN python -c "from data_source import CorpusFactory; CorpusFactory().recreate_corpus()"

COPY . .

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "main:server"]
