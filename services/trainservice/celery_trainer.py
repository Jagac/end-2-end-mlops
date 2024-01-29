from celery import Celery
from fp import DataHandler, TrainingHandler
from datetime import datetime
import pytz

ny_timezone = pytz.timezone("America/New_York")
ny_time = datetime.now(ny_timezone)
ny_date = ny_time.date()

trainer_celery = Celery(
    "celery_trainer", broker="redis://localhost:6379", backend="redis://localhost:6379"
)


@trainer_celery.task
def trigger_training_pipeline(data: dict) -> None:
    target = data.get("target")
    data_handler = DataHandler(target)

    df = data_handler.get_full()
    training_handler = TrainingHandler(df)
    training_handler.auto_train(
        registry_name=f"{target}-{ny_date}",
        num_trials=25,
        best_model_experiment_name="best_experiments"
    )
