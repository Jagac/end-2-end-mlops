import datetime
from typing import Callable

import mlflow
import optuna
import pandas as pd
from optuna.integration.mlflow import MLflowCallback
from prophet import Prophet
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

from .config import Config


class TrainingHandler:
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.config = Config()
        self.config.setup_environment()

    def auto_train(
        self,
        registry_name: str,
        num_trials: int,
        best_model_experiment_name: str,
    ) -> None:
        params = self._optimize_params(
            study_name="auto_train", num_trials=num_trials, objective=self._objective
        )

        train_df, val_df, test_df = self._split_data()
        mlflow.set_experiment(experiment_name=best_model_experiment_name)

        with mlflow.start_run():
            m = Prophet(**params)
            m.add_country_holidays(country_name="NL")
            m.fit(train_df)
            preds = m.predict(val_df[["ds", "cap", "floor"]])

            signature = mlflow.models.infer_signature(test_df["y"], preds["yhat"])

            mlflow.log_params(params)
            mlflow.log_metrics({"mse": mean_squared_error(test_df["y"], preds["yhat"])})
            mlflow.log_metrics({"r2": r2_score(test_df["y"], preds["yhat"])})
            mlflow.log_metrics(
                {"mape": mean_absolute_percentage_error(test_df["y"], preds["yhat"])}
            )

            mlflow.prophet.log_model(
                pr_model=m,
                artifact_path=f"prophet-model-{datetime.datetime.now()}",
                signature=signature,
                registered_model_name=f"{registry_name}",
            )

    def full_manual_train(
        self,
        changepoint_prior_scale,
        changepoint_range,
        seasonality_prior_scale,
        seasonality_mode,
        growth,
        weekly_seasonality,
        yearly_seasonality,
    ) -> None:
        params = {
            "changepoint_prior_scale": changepoint_prior_scale,
            "changepoint_range": changepoint_range,
            "seasonality_prior_scale": seasonality_prior_scale,
            "seasonality_mode": seasonality_mode,
            "growth": growth,
            "weekly_seasonality": weekly_seasonality,
            "yearly_seasonality": yearly_seasonality,
        }

        with mlflow.start_run():
            m = Prophet(**params)
            m.add_country_holidays(country_name="NL")
            m.fit(self.df)

            preds = m.predict(self.df[["ds", "cap", "floor"]])

            signature = mlflow.models.infer_signature(self.df["y"], preds["yhat"])
            mlflow.prophet.log_model(
                pr_model=m,
                artifact_path=f"prophet-model-{datetime.datetime.now()}",
                signature=signature,
                registered_model_name=f"Best fully trained",
            )

    @staticmethod
    def _optimize_params(study_name: str, num_trials: int, objective: Callable) -> dict:
        pruner = optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=5)
        study = optuna.create_study(
            study_name=study_name, direction="minimize", pruner=pruner
        )

        mlflow_callback = MLflowCallback(
            tracking_uri=mlflow.get_tracking_uri(), metric_name="rmse"
        )
        study.optimize(
            objective,
            n_trials=num_trials,
            callbacks=[mlflow_callback],
        )

        return study.best_trial.params

    def _objective(self, trial: optuna.trial) -> float | int:
        params = {
            "changepoint_prior_scale": trial.suggest_float(
                "changepoint_prior_scale", 0.005, 5
            ),
            "changepoint_range": trial.suggest_float("changepoint_range", 0.8, 0.9),
            "seasonality_prior_scale": trial.suggest_float(
                "seasonality_prior_scale", 0.1, 10
            ),
            "holidays_prior_scale": trial.suggest_float(
                "holidays_prior_scale", 0.1, 10
            ),
            "seasonality_mode": trial.suggest_categorical(
                "seasonality_mode", ["multiplicative", "additive"]
            ),
            "growth": trial.suggest_categorical("growth", ["linear", "logistic"]),
            "weekly_seasonality": trial.suggest_int("weekly_seasonality", 5, 10),
            "yearly_seasonality": trial.suggest_int("yearly_seasonality", 1, 20),
        }

        train_df, val_df, test_df = self._split_data()
        m = Prophet(**params)
        m.add_country_holidays(country_name="NL")
        m.fit(train_df)
        preds = m.predict(val_df[["ds", "cap", "floor"]])

        mae_score = mean_absolute_error(val_df["y"], preds["yhat"])
        return mae_score

    def _split_data(self):
        test_size = int(self.df.shape[0] / 10)
        train_df = self.df.iloc[: -2 * test_size, :]  # Train on 80% of data
        val_df = self.df.iloc[-2 * test_size : -test_size, :]  # Validate on 10% of data
        test_df = self.df.iloc[-test_size:, :]  # Test on remaining 10% of data

        return train_df, val_df, test_df
