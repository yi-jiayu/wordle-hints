FROM python:3.10-slim-buster

RUN apt-get update -y && apt-get upgrade -y

WORKDIR /app
COPY ["Pipfile", "Pipfile.lock", "./"]
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile

# Build cache, WORDLE_FOLDER determines where the wordle cache is stored. Path will be /app/.wordle
ENV WORDLE_FOLDER=/app
COPY ["corpus", "corpus"]
ENV GITHUB_SOURCE=1
RUN python -c "from corpus import CorpusFactory; CorpusFactory().recreate_data_files()"

COPY . .

ENTRYPOINT ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080"]
