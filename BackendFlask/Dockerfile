FROM python:3.7-alpine

ENV APPDIR=/home/app
ENV FLASK_APP=$APPDIR/lightword.py
COPY . $APPDIR

RUN apk --no-cache add build-base python3-dev py-gevent sox netcat-openbsd && \
    pip3 install --no-cache-dir -r $APPDIR/requirements.txt && \
    apk del python3-dev build-base

EXPOSE 5000
WORKDIR $APPDIR

ENTRYPOINT ["sh", "./entrypoint.sh"]