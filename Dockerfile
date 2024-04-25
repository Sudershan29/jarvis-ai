FROM python:3.8-slim-buster

WORKDIR /app

COPY ./jarvis-brain/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./jarvis-brain/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--log-level", "debug"]
