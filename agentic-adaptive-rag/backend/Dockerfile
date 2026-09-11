FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requriments.txt .

RUN pip install --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --default-timeout=1000 \
    --no-cache-dir \
    -r requriments.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8000","--reload"]