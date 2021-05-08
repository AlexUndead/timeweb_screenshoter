web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-5000}
main_worker: celery -A tasks worker -l info
