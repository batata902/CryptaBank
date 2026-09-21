#!/bin/sh

set -e

(
    cd /bank/bank/
    python3 main.py
) &

cd /bank/web/

exec python3 main.py