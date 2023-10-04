FROM python:3.9-alphine
WORKDIR /app

ENV PYTHONUNBUFFERED=1
 
COPY requirements.txt .

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps gcc libc-dev linux-headers postgresql-dev
RUN pip install -r requirements.txt
 
RUN apk del .tmp-build-dep
COPY . .
 
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
