# Dockerfile
FROM python:alpine3.7 
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt # Write Flask in this file
EXPOSE 8080 
ENTRYPOINT [ "python" ] 
CMD [ "run.py" ]