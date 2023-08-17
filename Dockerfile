FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /home/app
COPY ./pyproject.toml ./poetry.lock* init.sh ./

RUN pip install poetry
RUN poetry install

CMD ["./init.sh"]
