import pandas as pd


# Format rate table helper
def FormatRateDF(data):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be DataFrame")

    if data.shape[1] != 2:
        raise ValueError("DataFrame must have 2 columns")

    columns = data.columns

    # Get valid data
    # 1. Get valid years
    extractDF = data.copy()
    extractDF.dropna(inplace=True)
    extractDF["Year"] = extractDF[columns[0]].str.extract("(\d{4})")
    yearQuarter = extractDF["Year"].value_counts()
    validYears = yearQuarter[
        (yearQuarter == 4) | (yearQuarter.index == yearQuarter.index.max())
    ].index

    # 2. Get years with four quarters data
    extractDF = extractDF[extractDF["Year"].isin(validYears)]

    # 3. Remove gap years
    continuousYears = (
        extractDF["Year"].astype(int).diff().eq(0)
        | extractDF["Year"].astype(int).diff().eq(1)
        | extractDF["Year"].astype(int).diff().isna()
    )
    maxIndex = continuousYears[~continuousYears].index.max()

    if not pd.isna(maxIndex):
        extractDF = extractDF.iloc[maxIndex:]

    years = extractDF["Year"].unique()
    years = years[1 : len(years) - 3]
    extractDF = extractDF.drop(columns=["Year"])

    # 4. Caculate rate
    extractDF["Rate"] = extractDF[columns[1]].pct_change(periods=4)
    extractDF.dropna(inplace=True)
    extractDF.reset_index(drop=True, inplace=True)

    return years, extractDF


def SplitRateDF(data, start):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be DataFrame")

    if data.shape[1] != 3:
        raise ValueError("DataFrame must have 3 columns")

    if start not in data[data.columns[0]].str.extract("(\d{4})")[0].unique()[:-3]:
        return None

    df = data.copy()
    startIndex = df[df[df.columns[0]].str.contains(start)].index[0]
    endYear = int(start) + 3
    endIndex = df[df[df.columns[0]].str.contains(str(endYear))].index[-1]

    return df.iloc[startIndex : endIndex + 1]

def MoneyFormat(num):
    if pd.isna(num):
        return None
    else:
        # return "{:,.2f}".format(num).replace(",", "X").replace(".", ",").replace("X", ".")
        return num

def FormatRateTable(data):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be DataFrame")

    if data.shape[1] != 3:
        raise ValueError("DataFrame must have 3 columns")

    maxDF = len(data.index)
    q1 = {
        "quarter": "Quý 1",
    }
    q2 = {
        "quarter": "Quý 2",
    }
    q3 = {
        "quarter": "Quý 3",
    }
    q4 = {
        "quarter": "Quý 4",
    }
    header = []
    jsonData = [q1, q2, q3, q4]

    for i in range(0, maxDF, 4):
        year = data[data.columns[0]].iloc[i][3:]
        header.append(year)
        if i + 3 > maxDF - 1:
            for j in range(i, maxDF):
                if j - i == 0:
                    q1[year + " value"] = MoneyFormat(data[data.columns[1]].iloc[j])
                    q1[year + " rate"] = data[data.columns[2]].iloc[j]
                elif j - i == 1:
                    q2[year + " value"] = MoneyFormat(data[data.columns[1]].iloc[j])
                    q2[year + " rate"] = data[data.columns[2]].iloc[j]
                elif j - i == 2:
                    q3[year + " value"] = MoneyFormat(data[data.columns[1]].iloc[j])
                    q3[year + " rate"] = data[data.columns[2]].iloc[j]
        else:
            q1[year + " value"] = MoneyFormat(data[data.columns[1]].iloc[i])
            q1[year + " rate"] = data[data.columns[2]].iloc[i]
            q2[year + " value"] = MoneyFormat(data[data.columns[1]].iloc[i + 1])
            q2[year + " rate"] = data[data.columns[2]].iloc[i + 1]
            q3[year + " value"] = MoneyFormat(data[data.columns[1]].iloc[i + 2])
            q3[year + " rate"] = data[data.columns[2]].iloc[i + 2]
            q4[year + " value"] = MoneyFormat(data[data.columns[1]].iloc[i + 3])
            q4[year + " rate"] = data[data.columns[2]].iloc[i + 3]

    return [header, jsonData]


# Format balance sheet table helper
def FormatBSDF(data):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be DataFrame")

    extractDF = data.copy()
    extractDF = extractDF.iloc[
        [
            1,
            2,
            5,
            9,
            17,
            20,
            26,
            27,
            34,
            44,
            47,
            50,
            61,
            63,
            64,
            80,
            93,
            95,
            96,
            105,
            115,
        ]
    ]

    extractDF.reset_index(drop=True, inplace=True)
    extractDF.dropna(axis=1, inplace=True)

    return extractDF.columns.tolist()[1:], extractDF


def SplitBSDF(data, time):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be DataFrame")

    WHITE = 0
    GREEN = 1
    RED = -1

    df = data.copy()
    df = df[["Item", time]]
    df["Color"] = WHITE
    df["Note"] = ""

    for i in range(1, 6):
        if (df.iloc[i][time] / df.iloc[12][time]) > 0.1:
            df.at[i, "Color"] = GREEN
            df.at[i, "Note"] = (
                str(round(df.iloc[i][time] / df.iloc[12][time] * 100, 2))
                + "% Tổng tài sản"
            )

    for i in range(7, 12):
        if (df.iloc[i][time] / df.iloc[12][time]) > 0.1:
            df.at[i, "Color"] = GREEN
            df.at[i, "Note"] = (
                str(round(df.iloc[i][time] / df.iloc[12][time] * 100, 2))
                + "% Tổng tài sản"
            )

    if df.iloc[14][time] > (df.iloc[1][time] + df.iloc[2][time]):
        df.at[14, "Color"] = RED
        df.at[14, "Note"] = "Không thể thanh toán nợ ngắn nếu phải trả ngay"

    if (df.iloc[13][time] / df.iloc[12][time]) > 0.6:
        df.at[13, "Color"] = RED
        df.at[13, "Note"] = (
            str(round(df.iloc[13][time] / df.iloc[12][time] * 100, 2))
            + "% Tổng tài sản"
        )

    if (df.iloc[16][time] / df.iloc[12][time]) > 0.6:
        df.at[16, "Color"] = GREEN
        df.at[16, "Note"] = "Có khả năng chống chịu rủi ro"

    return df


def FormatBSTable(data):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be DataFrame")

    if data.shape[1] != 4:
        raise ValueError("DataFrame must have 4 columns")

    jsonData = [
        {
            "name-1": data.iloc[0]["Item"],
            "value-1": {
                "v": data.iloc[0][data.columns[1]],
                "c": data.iloc[0]["Color"],
            },
            "note-1": data.iloc[0]["Note"],
            "name-2": data.iloc[13]["Item"],
            "value-2": {
                "v": data.iloc[13][data.columns[1]],
                "c": data.iloc[13]["Color"],
            },
            "note-2": data.iloc[13]["Note"],
        }
    ]

    for i in range(1, 6):
        if i < 3:
            jsonData.append(
                {
                    "name-1": data.iloc[i]["Item"],
                    "value-1": {
                        "v": data.iloc[i][data.columns[1]],
                        "c": data.iloc[i]["Color"],
                    },
                    "note-1": data.iloc[i]["Note"],
                    "name-2": data.iloc[i + 13]["Item"],
                    "value-2": {
                        "v": data.iloc[i + 13][data.columns[1]],
                        "c": data.iloc[i + 13]["Color"],
                    },
                    "note-2": data.iloc[i + 13]["Note"],
                }
            )
        else:
            jsonData.append(
                {
                    "name-1": data.iloc[i]["Item"],
                    "value-1": {
                        "v": data.iloc[i][data.columns[1]],
                        "c": data.iloc[i]["Color"],
                    },
                    "note-1": data.iloc[i]["Note"],
                }
            )

    jsonData.append(
        {
            "name-1": data.iloc[6]["Item"],
            "value-1": {
                "v": data.iloc[6][data.columns[1]],
                "c": data.iloc[6]["Color"],
            },
            "note-1": data.iloc[6]["Note"],
            "name-2": data.iloc[16]["Item"],
            "value-2": {
                "v": data.iloc[16][data.columns[1]],
                "c": data.iloc[16]["Color"],
            },
            "note-2": data.iloc[16]["Note"],
        }
    )

    for i in range(7, 12):
        if i < 10:
            jsonData.append(
                {
                    "name-1": data.iloc[i]["Item"],
                    "value-1": {
                        "v": data.iloc[i][data.columns[1]],
                        "c": data.iloc[i]["Color"],
                    },
                    "note-1": data.iloc[i]["Note"],
                    "name-2": data.iloc[i + 10]["Item"],
                    "value-2": {
                        "v": data.iloc[i + 10][data.columns[1]],
                        "c": data.iloc[i + 10]["Color"],
                    },
                    "note-2": data.iloc[i + 10]["Note"],
                }
            )
        else:
            jsonData.append(
                {
                    "name-1": data.iloc[i]["Item"],
                    "value-1": {
                        "v": data.iloc[i][data.columns[1]],
                        "c": data.iloc[i]["Color"],
                    },
                    "note-1": data.iloc[i]["Note"],
                }
            )

    jsonData.append(
        {
            "name-1": data.iloc[12]["Item"],
            "value-1": {
                "v": data.iloc[12][data.columns[1]],
                "c": data.iloc[12]["Color"],
            },
            "note-1": data.iloc[12]["Note"],
            "name-2": data.iloc[20]["Item"],
            "value-2": {
                "v": data.iloc[20][data.columns[1]],
                "c": data.iloc[20]["Color"],
            },
            "note-2": data.iloc[20]["Note"],
        }
    )

    return jsonData