import modules.preprocess as pp

stock = [
    "CKV",
    "CMG",
    "ELC",
    "FPT",
    "HIG",
    "ITD",
    "KST",
    "ONE",
    "POT",
    "SAM",
    "SGT",
    "SMT",
    "SRA",
    "ST8",
    "UNI",
    "VLA",
]

PreprocessHelper = pp.PreprocessHelper()

for i in stock:
    print(
        i + ":", PreprocessHelper.LoadCSV("./data/" + i + "/NPAT_Q.csv").GetValidYears()
    )

print(
    PreprocessHelper.LoadCSV("./data/FPT/NPAT_Q.csv").DropMissingData().GetDataFrame()
)
