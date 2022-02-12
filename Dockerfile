FROM python:3.10-buster

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "./"]
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile

# Build cache
COPY ["data_source.py", "./"]
RUN python data_source.py

COPY . .

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:80", "main:server"]
