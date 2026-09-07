FROM python:3.14

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY vectorstore.json /code

COPY *.py /code

CMD ["fastapi", "run", "query.py", "--port", "8000"]