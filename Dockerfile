FROM ankitmhjn5/python_nltk

WORKDIR /backend_app

COPY ./requirements.txt /backend_app/requirements.txt

COPY pdf /backend_app/pdf

RUN pip install --no-cache-dir -r /backend_app/requirements.txt
ENV API_KEY=

COPY ./app /backend_app/app

EXPOSE 8080

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080" ]

