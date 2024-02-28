from tasks.factory import LpgTask

if __name__ == "__main__":
    lpg_celery = LpgTask().fuel_task()
    lpg_celery.worker_main(["-Q", "lpg_queue", "--loglevel=INFO"])
