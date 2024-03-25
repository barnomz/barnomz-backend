FROM python:3.10.5-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

#RUN apt-get update && apt-get install cron -y && apt install nano
#COPY ./cronjobs/crontab /etc/cron.d
#RUN chmod 0644 /etc/cron.d/crontab
#RUN crontab /etc/cron.d/crontab
#RUN touch /var/log/cron.log

COPY . /app

RUN mkdir -p /app/run
RUN mkdir -p /var/log/gunicorn/

RUN touch /var/log/gunicorn/access.log
RUN touch /var/log/gunicorn/error.log

EXPOSE 8000

CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
