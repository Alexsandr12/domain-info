FROM python:3.8-alpine

COPY . ./app

RUN pip install --upgrade pip \
&& pip install --no-cache-dir -r /app/requirements.txt \
&& pip install mysql-connector-python

EXPOSE 5000

CMD python /app/web.py
