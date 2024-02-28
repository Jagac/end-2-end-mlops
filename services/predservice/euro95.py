from tasks.factory import Euro95Task

if __name__ == "__main__":
    diesel_celery = Euro95Task().fuel_task()
    diesel_celery.worker_main(["-Q", "diesel_queue", "--loglevel=INFO"])
