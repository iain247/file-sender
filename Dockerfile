FROM python:3
WORKDIR /file_sender
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]