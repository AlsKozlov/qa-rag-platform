FROM python:3.11

RUN mkdir /stt_service

WORKDIR /stt_service

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

COPY . .
