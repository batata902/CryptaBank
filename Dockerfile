FROM python:3.12-slim

RUN apt-get update && apt-get upgrade -y && apt-get install netcat-openbsd net-tools

WORKDIR /bank

COPY bank ./bank
COPY web ./web

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 5000

CMD ["./entrypoint.sh"]
