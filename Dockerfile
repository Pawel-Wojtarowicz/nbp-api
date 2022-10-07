FROM python:3.10

WORKDIR /app
COPY . /app
ADD app.py .
ADD credentials.py .

RUN pip install boto3
CMD ["python", "app.py"]