from datetime import datetime

import pandas as pd
import pytz
from celery import Celery
from train import TrainingStrategyBuilder

ny_timezone = pytz.timezone("America/New_York")
ny_time = datetime.now(ny_timezone)
ny_date = ny_time.date()

trainer_celery = Celery(
    "celery_trainer", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)


@trainer_celery.task
def trigger_training_pipeline(data, target) -> None:
    df = pd.DataFrame(data)

    auto_trainer = (
        TrainingStrategyBuilder(df)
        .set_auto_training_params(f"{target}-{ny_date}", 3, "best_experiments")
        .build_auto_trainer()
    )
    auto_trainer.train()
