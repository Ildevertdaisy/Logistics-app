
FROM python:3.10

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./models /app/models/
COPY ./database.py /app/database.py
COPY ./db_connection.py /app/db_connection.py 
COPY ./app.py /app/app.py

EXPOSE 8001

CMD ["uvicorn", "app:app", "--port", "8001", "--host", "0.0.0.0", "--reload"]