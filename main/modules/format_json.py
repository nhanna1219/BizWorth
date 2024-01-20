import pandas as pd
import re

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

# Format business result table helper
def FormatBRDF(dataBOR, dataME, returnTime):
    if not isinstance(dataBOR, pd.DataFrame):
        raise ValueError("Data BOR must be DataFrame")

    if not isinstance(dataME, pd.DataFrame):
        raise ValueError("Data ME must be DataFrame")

    borDF = dataBOR.copy()
    borDF = borDF.iloc[0:20]
    meDF = dataME.copy()
    meDFTransposed = meDF.T
    meDFTransposed.columns = meDFTransposed.iloc[0]
    meDFTransposed = meDFTransposed[1:]
    meDFTransposed.reset_index(inplace=True)
    meDFTransposed.columns.name = None
    meDFTransposed.rename(columns={"index": "Item"}, inplace=True)
    meDFTransposed["Item"] = "20. " + meDFTransposed["Item"]
    meDFTransposed.columns = meDFTransposed.columns.str.strip()
    extractDF = pd.concat([borDF, meDFTransposed], axis=0, ignore_index=True)
    extractDF.dropna(axis=1, inplace=True)

    time = []

    if returnTime:
        for i in range(1, len(extractDF.columns)):
            currentCol = extractDF.columns[i]
            previousCol = f"{extractDF.columns[i].split()[0]} {int(extractDF.columns[i].split()[1]) - 1}"

            if previousCol in extractDF.columns:
                time.append(currentCol)

    return time, extractDF


def EvaluateField(df, i, pos):
    GREEN = 1
    RED = -1

    for j in [1, 3, 6, 9, 10, 13, 16, 17, 18]:
        if df.iloc[j][i] <= 0:
            df.at[j, "Color-" + pos] = GREEN

    for j in [2, 4, 5, 8, 11, 12, 14, 15, 19]:
        if df.iloc[j][i] <= 0:
            df.at[j, "Color-" + pos] = RED

    if (df.iloc[1][i] / df.iloc[0][i]) > 0.2:
        df.at[1, "Color-" + pos] = RED

    if (df.iloc[3][i] / df.iloc[2][i]) > 0.65:
        df.at[3, "Color-" + pos] = RED

    if (df.iloc[6][i] / df.iloc[0][i]) > 0.05:
        df.at[6, "Color-" + pos] = RED

    if df.iloc[20][i] > 0:
        df.at[20, "Color-" + pos] = GREEN
        df.at[20, "Note-" + pos] = "Doanh nghiệp có khả năng trả nợ"
    else:
        df.at[20, "Color-" + pos] = RED
        df.at[20, "Note-" + pos] = "Doanh nghiệp không có khả năng trả nợ"

    for j in range(1, 20):
        df.at[j, "Note-" + pos] = (
            str(round(df.iloc[j][i] / df.iloc[0][i] * 100, 4)) + "% Tổng doanh thu"
        )


def SplitBRDF(data, time):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be DataFrame")

    WHITE = 0
    df = data.copy()
    previousCol = f"{time.split()[0]} {int(time.split()[1]) - 1}"

    df = df[["Item", previousCol, time]]
    df["Color-1"] = WHITE
    df["Note-1"] = ""
    df["Color-2"] = WHITE
    df["Note-2"] = ""
    EvaluateField(df, previousCol, "1")
    EvaluateField(df, time, "2")

    df[previousCol] = df[previousCol].astype(float)
    df[time] = df[time].astype(float)
    df["Color-1"] = df["Color-1"].astype(float)
    df["Color-2"] = df["Color-2"].astype(float)

    return df


def FormatBRTable(data):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be DataFrame")

    if data.shape[1] != 7:
        raise ValueError("DataFrame must have 7 columns")

    header = [data.columns[1], data.columns[2]]
    jsonData = []

    for i in data.index:
        jsonData.append(
            {
                "name": data.iloc[i]["Item"],
                "value-1": data.iloc[i][data.columns[1]],
                "note-1": {"v": data.iloc[i]["Note-1"], "c": data.iloc[i]["Color-1"]},
                "value-2": data.iloc[i][data.columns[2]],
                "note-2": {
                    "v": data.iloc[i]["Note-2"],
                    "c": data.iloc[i]["Color-2"],
                },
            }
        )

    return [header, jsonData]


# Format financial index table helper
def sortSetDataTime(entry):
    quarter, year = entry.split()
    return year, int(quarter[1])

def GetFIOptions(tickerData):
    convertFormat = lambda x: re.sub(r"(\d+) - Q(\d+)", r"Q\2 \1", x)
    data = []
    for index in range(0, len(tickerData)):
        data.append(
            [i.replace("/", " ") for i in tickerData[index].Sales_Q["Date"].to_list()]
        )
        data.append(
            [i.replace("/", " ") for i in tickerData[index].NPAT_Q["Date"].to_list()]
        )
        data.append(tickerData[index].balanceSheet.columns[1:].to_list())
        data.append(
            tickerData[index]
            .FinancialReport_Q["Duration"]
            .apply(convertFormat)
            .to_list()
        )

    df = pd.DataFrame(data)
    intersectionYears = set(df.iloc[0].dropna())
    for i in range(1, len(df.index)):
        intersectionYears = intersectionYears.intersection(set(df.iloc[i].dropna()))

    sortedYears = sorted(intersectionYears, key=sortSetDataTime)
    
    # ITD, CMG Q2 2023
    return sortedYears


def FormatFITable(tickerData, tickerNames, time):
    eps, dt_kpt, ts_nn, vqtsn, ros = (
        {"index": "EPS"},
        {"index": "DT/Khoản phải thu"},
        {"index": "TS có thanh khoản cao/Nợ ngắn"},
        {"index": "Vòng quay TS ngắn"},
        {"index": "ROS"},
    )
    
    roa, roe, roic, n_ts, dbtc = (
        {"index": "ROA"},
        {"index": "ROE"},
        {"index": "ROIC"},
        {"index": "Nợ/TS"},
        {"index": "Đòn bẩy tài chính"},
    )
    
    jsonData = [eps, dt_kpt, ts_nn, vqtsn, ros, roa, roe, roic, n_ts, dbtc]
    quarter, year = time.split()

    for index in range(0, len(tickerData)):
        sales = tickerData[index].Sales_Q
        npat = tickerData[index].NPAT_Q
        bs = tickerData[index].balanceSheet
        financialReport = tickerData[index].FinancialReport_Q

        eps[tickerNames[index]] = financialReport.loc[
            financialReport["Duration"] == f"{year} - {quarter}", "EPS"
        ].values[0]

        if ((bs.loc[bs["Item"] == "III. Các khoản phải thu ngắn hạn", time].values[0] + 
             bs.loc[bs["Item"] == "I. Các khoản phải thu dài hạn", time].values[0]) != 0):
            dt_kpt[tickerNames[index]] = sales.loc[
                sales["Date"] == f"{quarter}/{year}", "Sales"
            ].values[0] / (
                bs.loc[bs["Item"] == "III. Các khoản phải thu ngắn hạn", time].values[0]
                + bs.loc[bs["Item"] == "I. Các khoản phải thu dài hạn", time].values[0]
            )
        else:
            dt_kpt[tickerNames[index]] = 0

        if (bs.loc[bs["Item"] == "I. Nợ ngắn hạn", time].values[0] != 0):
            ts_nn[tickerNames[index]] = (
                bs.loc[bs["Item"] == "I. Tiền và các khoản tương đương tiền", time].values[
                    0
                ]
                / bs.loc[bs["Item"] == "I. Nợ ngắn hạn", time].values[0]
            )
        else:
            ts_nn[tickerNames[index]] = 0

        if (bs.loc[bs["Item"] == "A. Tài sản lưu động và đầu tư ngắn hạn", time].values[0] != 0):
            vqtsn[tickerNames[index]] = (sales.loc[sales["Date"] == f"{quarter}/{year}", "Sales"].values[0]
                / bs.loc[
                    bs["Item"] == "A. Tài sản lưu động và đầu tư ngắn hạn", time
                ].values[0]
            )
        else:
            vqtsn[tickerNames[index]] = 0

        if (sales.loc[sales["Date"] == f"{quarter}/{year}", "Sales"].values[0] != 0):
            ros[tickerNames[index]] = (
                npat.loc[npat["Date"] == f"{quarter}/{year}", "NOPAT"].values[0] * 1e9
            ) / sales.loc[sales["Date"] == f"{quarter}/{year}", "Sales"].values[0]
        else:
            ros[tickerNames[index]] = 0

        if (bs.loc[bs["Item"] == "TỔNG CỘNG TÀI SẢN", time].values[0] != 0):
            roa[tickerNames[index]] = (
                npat.loc[npat["Date"] == f"{quarter}/{year}", "NOPAT"].values[0] * 1e9
            ) / bs.loc[bs["Item"] == "TỔNG CỘNG TÀI SẢN", time].values[0]
        else:
            roa[tickerNames[index]] = 0

        if (bs.loc[bs["Item"] == "B. Nguồn vốn chủ sở hữu", time].values[0] != 0):
            roe[tickerNames[index]] = (
                npat.loc[npat["Date"] == f"{quarter}/{year}", "NOPAT"].values[0] * 1e9
            ) / bs.loc[bs["Item"] == "B. Nguồn vốn chủ sở hữu", time].values[0]
        else:
            roe[tickerNames[index]] = 0

        if ((
                bs.loc[bs["Item"] == "B. Nguồn vốn chủ sở hữu", time].values[0]
                + bs.loc[bs["Item"] == "II. Nợ dài hạn", time].values[0]
            ) != 0):
            roic[tickerNames[index]] = (
                npat.loc[npat["Date"] == f"{quarter}/{year}", "NOPAT"].values[0] * 1e9
            ) / (
                bs.loc[bs["Item"] == "B. Nguồn vốn chủ sở hữu", time].values[0]
                + bs.loc[bs["Item"] == "II. Nợ dài hạn", time].values[0]
            )
        else:
            roic[tickerNames[index]] = 0

        n_ts[tickerNames[index]] = (
            bs.loc[bs["Item"] == "A. Nợ phải trả", time].values[0]
            / bs.loc[bs["Item"] == "TỔNG CỘNG TÀI SẢN", time].values[0]
        )

        if (bs.loc[bs["Item"] == "B. Nguồn vốn chủ sở hữu", time].values[0] != 0):
            dbtc[tickerNames[index]] = (
                bs.loc[bs["Item"] == "TỔNG CỘNG TÀI SẢN", time].values[0]
                / bs.loc[bs["Item"] == "B. Nguồn vốn chủ sở hữu", time].values[0]
            )
        else:
            dbtc[tickerNames[index]] = 0

    return jsonData