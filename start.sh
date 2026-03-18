#!/bin/bash
cd /run/media/nagat/Storage/univer/BD/bd-hospital
source venv/bin/activate
sudo systemctl start postgresql
echo "Запуск сервера на http://127.0.0.1:8080"
uvicorn backend.main:app --reload --port 8080
