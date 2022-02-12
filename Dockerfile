FROM python:3.10-slim-buster

WORKDIR /app

RUN apt-get update -y && apt-get upgrade -y

COPY ["Pipfile", "Pipfile.lock", "./"]
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile

# Build cache
COPY ["data_source.py", "./"]
RUN python data_source.py

COPY . .

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "main:server"]
