FROM python:3.11

RUN mkdir /llm_app

WORKDIR /llm_app

COPY requirements.txt .

RUN apt-get update && apt-get install -y python3-pip

RUN pip install -r requirements.txt

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY . .