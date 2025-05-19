mkdir gunicorn.data &> /dev/null
pkill gunicorn
sleep 2
source .venv/bin/activate && \
    source .env && \
    gunicorn translator.wsgi --daemon \
     --pid gunicorn.data/gunicorn.pid \
     --reload \
     --access-logfile gunicorn.data/access.log \
     --error-logfile gunicorn.data/error.log \
     --workers 4