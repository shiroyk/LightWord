#!/bin/sh

while ! nc -z db 3306; do sleep 3; done

echo "App can connect db!"

while ! nc -z redis 6379; do sleep 3; done

echo "App can connect redis!"

sleep 1 && echo "Run init db." && flask initdb

if [ $? == 0 ]; then
    flask vocabulary --path resources/vocabulary.csv && flask vocabdata --path resources/GRE_Abridged.txt || echo "Database initialization failed!!!"
else
    echo "Database doesn't need to be initialized."
fi

echo "Run migrations." && flask db upgrade || echo "Upgrade db failed."

gunicorn -c config/gunicorn.py lightword:app --log-config config/logging.conf