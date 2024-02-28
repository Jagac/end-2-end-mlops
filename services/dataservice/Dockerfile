FROM python:3.10-alpine

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt
COPY . /code

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:3000", "wsgi:app"]