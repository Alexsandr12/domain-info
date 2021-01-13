FROM python:3.8-alpine

COPY . ./app

RUN pip install --upgrade pip \
&& pip install --no-cache-dir -r /app/requirements.txt \
&& --name some-mariadb -e MYSQL_ROOT_PASSWORD=1 -d mariadb

CMD python /app/web.py
