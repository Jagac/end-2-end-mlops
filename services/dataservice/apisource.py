from datetime import datetime

import pandas as pd
import requests


class DataHandler:
    """Handles data from the api"""

    def __init__(self, target_column: str) -> None:
        """
        Args:
            target_column (str): euro95_1 / diesel_2 / lpg_3
        """
        self.url = "https://opendata.cbs.nl/ODataApi/odata/80416ENG/TypedDataSet"
        self.target_column = target_column
        self.cap = None
        self.floor = None

    def get_full(self) -> pd.DataFrame:

        data = requests.get(self.url)

        data = data.json()["value"]
        df = pd.DataFrame().from_dict(data)
        df = self._prepare_dataframe(df)
        latest_date = df.ds.max()
        return df, latest_date

    def get_latest(self) -> pd.DataFrame:
        data = requests.get(self.url)
        data = data.json()["value"]
        df = pd.DataFrame().from_dict(data)
        df = self._prepare_dataframe(df)

        today = datetime.now().strftime("%Y%m%d")
        filtered_df = df[df["ds"] == today]

        return filtered_df

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [col.lower() for col in df.columns]
        df = df.rename(columns={"periods": "ds", f"{self.target_column}": "y"})

        for i in df.columns:
            if i == "y" or i == "ds":
                pass
            else:
                df = df.drop(i, axis=1)
                print(i)

        self.cap = df["y"].max()
        self.floor = df["y"].min()

        df["cap"] = self.cap
        df["floor"] = self.floor

        return df
