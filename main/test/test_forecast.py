import main.modules.forecast as fc
import main.common.const as const

# Create helper and Load CSV
ForecastHelper = fc.ForecastHelper()
ForecastHelper.LoadCSV("NPAT_Q.csv")

# Format Date column
ForecastHelper.FormatDate(const.DATE_MODE)
# ForecastHelper.FormatDate(const.QUARTER_MODE)

# Get DataFrame from helper
df = ForecastHelper.GetDataFrame().head(15)

# Generate Model and save
ForecastHelper.GenerateModel(10, 10)
model = ForecastHelper.GetModel()
print(model)
ForecastHelper.SaveModel("./","test_model")

# Load model and forecast
ForecastHelper.LoadModel("./test_model.pkl")
print(ForecastHelper.Forecast(8, const.QUARTER_MODE))