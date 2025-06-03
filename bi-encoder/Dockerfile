FROM python:3.10

RUN mkdir /bi_encoder

WORKDIR /bi_encoder

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .