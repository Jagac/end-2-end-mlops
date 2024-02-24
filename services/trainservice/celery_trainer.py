from celery import Celery
from train import TrainingHandler
from datetime import datetime
import pytz
import pandas as pd

ny_timezone = pytz.timezone("America/New_York")
ny_time = datetime.now(ny_timezone)
ny_date = ny_time.date()

trainer_celery = Celery(
    "celery_trainer", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)

@trainer_celery.task
def trigger_training_pipeline(data, target) -> None:
    df = pd.DataFrame(data)
    
    training_handler = TrainingHandler(df)
    training_handler.auto_train(
        registry_name=f"{target}-{ny_date}",
        num_trials=25,
        best_model_experiment_name="best_experiments",
    )
