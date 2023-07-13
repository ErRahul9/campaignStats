FROM python:3.10-slim-buster
RUN mkdir /app

WORKDIR /app
COPY . /app
COPY pyproject.toml ./


RUN pip install --upgrade pip setuptools

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential
RUN apt-get install -y libpq-dev



ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip install pandas==2.0.2
RUN pip install statsmodels==0.14.0
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

CMD ["poetry", "run", "python", "campaign/main.py", "20708","2023-06-15", "2023-06-23"]