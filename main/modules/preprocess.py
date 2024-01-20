import pandas as pd
import os


class PreprocessHelper:
    def __init__(self):
        self.__DataFrame = None

    def __GetValidYears(self):
        df = self.__DataFrame.copy()
        df["Year"] = df["Date"].str.extract("(\d{4})")
        yearQuarter = df["Year"].value_counts()
        return yearQuarter[
            (yearQuarter == 4) | (yearQuarter.index == yearQuarter.index.max())
        ].index

    def LoadCSV(self, path):
        if not isinstance(path, str):
            raise ValueError("Please provide a string")

        if path.endswith(".csv") == False:
            raise ValueError("Please provide a csv file")

        df = pd.read_csv(path)

        if "Date" not in df.columns:
            raise ValueError("Date column not found")

        if "NOPAT" not in df.columns:
            raise ValueError("NOPAT column not found")

        self.__DataFrame = df
        return self

    def SaveCSV(self, path, name):
        if self.__DataFrame is None:
            raise ValueError("Dataframe not loaded")

        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")

        if "/" in name or "." in name:
            raise ValueError("Name must not contain '/' or '.'")

        self.__DataFrame.to_csv(path + name + ".csv", index=False)

    def SetDataFrame(self, df):
        if "Date" not in df.columns:
            raise ValueError("Date column not found")

        if "NOPAT" not in df.columns:
            raise ValueError("NOPAT column not found")

        self.__DataFrame = df
        return self

    def GetDataFrame(self):
        if self.__DataFrame is None:
            raise ValueError("Dataframe not loaded")

        return self.__DataFrame

    def GetValidYears(self):
        if self.__DataFrame is None:
            raise ValueError("Dataframe not loaded")

        return self.__GetValidYears().to_list()

    def DropMissingData(self):
        if self.__DataFrame is None:
            raise ValueError("Dataframe not loaded")

        validYears = self.__GetValidYears()
        self.__DataFrame["Year"] = self.__DataFrame["Date"].str.extract("(\d{4})")
        self.__DataFrame = self.__DataFrame[self.__DataFrame["Year"].isin(validYears)]
        self.__DataFrame = self.__DataFrame.drop(columns=["Year"])
        self.__DataFrame.reset_index(drop=True, inplace=True)
        return self

    def DropGapYears(self):
        if self.__DataFrame is None:
            raise ValueError("Dataframe not loaded")

        self.__DataFrame["Year"] = self.__DataFrame["Date"].str.extract("(\d{4})")
        continuousYears = (
            self.__DataFrame["Year"].astype(int).diff().eq(0)
            | self.__DataFrame["Year"].astype(int).diff().eq(1)
            | self.__DataFrame["Year"].astype(int).diff().isna()
        )
        maxIndex = continuousYears[~continuousYears].index.max()
        self.__DataFrame = self.__DataFrame.iloc[maxIndex:]
        self.__DataFrame = self.__DataFrame.drop(columns=["Year"])
        self.__DataFrame.reset_index(drop=True, inplace=True)
        return self
