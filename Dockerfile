FROM python:3.9

WORKDIR /backend_app

COPY ./requirements.txt /backend_app/requirements.txt

COPY pdf /backend_app/pdf

RUN pip install -r /backend_app/requirements.txt

RUN [ "python", "-c", "import nltk; nltk.download('all')" ]

COPY ./app /backend_app/app

EXPOSE 8080

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080" ]

