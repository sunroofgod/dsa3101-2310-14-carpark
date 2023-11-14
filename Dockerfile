FROM python:3.10.6-slim-buster

WORKDIR /app

COPY backend/ backend/
COPY frontend/ frontend/
COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Expose port which Dash will work on
EXPOSE 8050 

CMD ["python", "frontend/app.py"]