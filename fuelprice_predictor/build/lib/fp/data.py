from datetime import datetime

import pandas as pd
import requests


class DataHandler:
    def __init__(self, target_column: str) -> None:
        self.url = "https://opendata.cbs.nl/ODataApi/odata/80416ENG/TypedDataSet"
        self.target_column = target_column
        self.cap = None
        self.floor = None

    def get_full(self) -> pd.DataFrame:
        data = requests.get(self.url)

        data = data.json()["value"]
        df = pd.DataFrame().from_dict(data)
        df = self._prepare_dataframe(df)
        print(df)

        return df

    def get_latest(self) -> pd.DataFrame:
        data = requests.get(self.url)
        data = data.json()["value"]
        df = pd.DataFrame().from_dict(data)
        df = self._prepare_dataframe(df)

        today = datetime.now().strftime("%Y%m%d")
        filtered_df = df[df["Periods"] == today]

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
