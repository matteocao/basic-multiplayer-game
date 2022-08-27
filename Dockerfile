FROM python:3.9-bullseye

COPY . .
RUN pip install -r requirements.txt

EXPOSE 5555

CMD ["python", "server.py"]