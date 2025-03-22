FROM python:3.12-slim-buster
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]
EXPOSE 3478