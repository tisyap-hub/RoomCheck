FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py database.py conflict_detector.py room_suggestions.py validator.py ./
COPY data/ ./data/

RUN python -c "from database import create_database, add_sample_rooms; create_database(); add_sample_rooms()"

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
