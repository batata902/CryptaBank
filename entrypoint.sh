#!/bin/sh

set -e

echo "Iniciando serviço local..."

(
    cd /bank/bank
    python3 main.py
) &

SERVICE_PID=$!

echo "Serviço iniciado: $SERVICE_PID"

echo "Iniciando aplicação web..."

cd /bank/web

exec python3 main.py