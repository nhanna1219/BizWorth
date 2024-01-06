import os
import pandas as pd
import re
import joblib
import statsmodels.api as sm
import main.common.const as const
import pmdarima
import warnings
import statsmodels.tsa.holtwinters.results as result
from math import sqrt
from sklearn.metrics import mean_squared_error
from pmdarima.arima import auto_arima
from statsmodels.tsa.stattools import adfuller
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pmdarima.model_selection import train_test_split
from statsmodels.tsa.api import ExponentialSmoothing

class ForecastHelper:

    def __init__(self):
        self.__DataFrame = None
        self.__Model = None
    
    def __CheckStationarity(self, series):
        result = adfuller(series.values)
        
        if (result[1] <= 0.05) & (result[4]['5%'] > result[0]):
            return True
        else:
            return False
        
    def __CalRMSE(self, actual, predicted):
        return sqrt(mean_squared_error(actual, predicted))
    
    def __GenerateArimaModel(self, data, config):
        param_p, param_d, param_q, param_m = config
        return auto_arima(data, start_p=0, start_q=0, max_p=param_p, max_q=param_q, d=param_d, m=param_m)
        
    def __GetBestD(self, max=5):
        for i in range(max+1):
            df = self.__DataFrame["NOPAT"]
            
            if i != 0:
                df = df.diff(i)
            
            if self.__CheckStationarity(df.dropna()):
                return i
        return None
    
    def __GetBestP(self, d=0):
        if d == 0:
            pacf, ci = sm.tsa.pacf(self.__DataFrame["NOPAT"].dropna(), alpha=0.05)
        else:
            pacf, ci = sm.tsa.pacf(self.__DataFrame["NOPAT"].diff(d).dropna(), alpha=0.05)
            
        for i in range(1, len(pacf)):
            if pacf[i] >= (ci[1][0] - pacf[1]) and pacf[i] <= (ci[1][1] - pacf[1]):
                return i - 1
        return None
    
    def __GetBestQ(self, d=0):
        if d == 0:
            acf, ci = sm.tsa.acf(self.__DataFrame["NOPAT"].dropna(), alpha=0.05)
        else:
            acf, ci = sm.tsa.acf(self.__DataFrame["NOPAT"].diff(d).dropna(), alpha=0.05)
            
        for i in range(1, len(acf)):
            if acf[i] >= (ci[1][0] - acf[1]) and acf[i] <= (ci[1][1] - acf[1]):
                return i - 1
        return None
    
    def __GetBestM(self, train, test, config=[0, 0, 0], max=1):
        param_p, param_d, param_q = config
        listModel = []
        
        for i in range(1,max+1):
            model = self.__GenerateArimaModel(train, [param_p, param_d, param_q, i])
            pred = model.predict(n_periods=len(test))
            listModel.append([i, self.__CalRMSE(test, pred)])
            
        return min(listModel, key=lambda x: x[1])[0]
        
    def __GenerateExpSmoothingConfigs(self, max_seasonal=2):
        if max_seasonal < 2:
            raise ValueError("seasonal must be greater than 2")
        
        Cfgs = list()
        t_params = ['add', 'mul', None]
        d_params = [True, False]
        s_params = ['add', 'mul', None]
        p_params = [None, *list(range(2, max_seasonal + 1))]
        b_params = [True, False]
        
        for t in t_params:
            for d in d_params:
                for s in s_params:
                    for p in p_params:
                        for b in b_params:
                                cfg = [t,d,s,p,b]
                                Cfgs.append(cfg)
        return Cfgs
    
    def __GenerateExpSmoothingModel(self, data, config):
        t, d, s, p, b = config
        return ExponentialSmoothing(data, trend=t, damped_trend=d, seasonal=s, seasonal_periods=p, use_boxcox=b).fit()
    
    def __ScoreExpSmoothingModel(self, train, test, cfg):
        try:
            result = self.__CalRMSE(test, self.__GenerateExpSmoothingModel(train, cfg).forecast(len(test)))
            return (cfg, result)
        except ValueError as err:
            return (cfg, None)
    
    def __GridSearchExpSmoothing(self, train, test, cfg_list):
        scores = None
        scores = [self.__ScoreExpSmoothingModel(train, test, cfg) for cfg in cfg_list]
        scores = [r for r in scores if r[1] != None]
        return min(scores, key=lambda x: x[1])[0]
    
    def __GetBestModel(self, test, listModel=[]):
        scores = []
        for i in listModel:
            if isinstance(i, pmdarima.arima.ARIMA):
                pred = i.predict(n_periods=len(test))
            else:
                pred = i.forecast(len(test))
            scores.append((i, self.__CalRMSE(test, pred)))
        
        bestModel = min(scores, key=lambda x: x[1])[0]
        
        if isinstance(bestModel, pmdarima.arima.ARIMA):
            return const.ARIMA_MODEL
        else:
            return const.EXPONENTIAL_SMOOTHING_MODEL
        
    def LoadCSV(self, path):
        if not isinstance(path, str):
            raise ValueError("Please provide a string")
        
        if path.endswith(".csv") == False:
            raise ValueError("Please provide a csv file")
        
        df = pd.read_csv(path)
        
        if 'Date' not in df.columns:
            raise ValueError("Date column not found")
        
        if 'NOPAT' not in df.columns:
            raise ValueError("NOPAT column not found")
        
        self.__DataFrame = df
        
    def SetDataFrame(self, df):
        if 'Date' not in df.columns:
            raise ValueError("Date column not found")
        
        if 'NOPAT' not in df.columns:
            raise ValueError("NOPAT column not found")
        
        self.__DataFrame = df
        
    def GetDataFrame(self):
        if self.__DataFrame is None:
            raise ValueError("Dataframe not loaded")
        
        return self.__DataFrame
    
    def FormatDate(self, mode):
        if self.__DataFrame is None:
            raise ValueError("Dataframe not loaded")
        
        if mode != const.DATE_MODE and mode != const.QUARTER_MODE:
            raise ValueError("Mode must be 'date' or 'quarter'")
        
        if mode == const.DATE_MODE:
            if not isinstance(self.__DataFrame["Date"], object):
                raise ValueError("Date must be an object")
            convert_format = lambda x: re.sub(r'Q(\d+)/(\d+)', r'\2-Q\1', x)
            self.__DataFrame["Date"] = self.__DataFrame["Date"].apply(convert_format)
            self.__DataFrame["Date"] = pd.PeriodIndex(self.__DataFrame["Date"], freq='Q').to_timestamp()
        else:
            if not is_datetime(self.__DataFrame["Date"]):
                raise ValueError("Date must be a datetime")
            
            self.__DataFrame["Date"] = self.__DataFrame["Date"].dt.to_period('Q').dt.strftime('Q%q/%Y')
            
    def GenerateModel(self, max_d=5, max_seasonal=2, warning_ignore=True):
        if self.__DataFrame is None:
            raise ValueError("Dataframe not loaded")
        
        if not is_datetime(self.__DataFrame["Date"]):
            raise ValueError("Date must be a datetime")
        
        if warning_ignore:
            warnings.filterwarnings('ignore')
        
        self.__DataFrame = self.__DataFrame.set_index('Date')
        self.__DataFrame.index = pd.date_range(start=self.__DataFrame.index[0] , periods=len(self.__DataFrame), freq='QS')
        
        train, test = train_test_split(self.__DataFrame)
        
        # Get best config for arima
        param_d = self.__GetBestD(max_d)
        param_p = self.__GetBestP(param_d)
        param_q = self.__GetBestQ(param_d)
        param_m = self.__GetBestM(train, test, [param_p, param_d, param_q], max_seasonal)
        bestConfigArima = [param_p, param_d, param_q, param_m]
        
        # Get best config for ETS
        etsTestConfigs = self.__GenerateExpSmoothingConfigs(max_seasonal)
        bestConfigETS = self.__GridSearchExpSmoothing(train, test, etsTestConfigs)

        # compare arima and ets
        bestModelType = self.__GetBestModel(test, [self.__GenerateArimaModel(train, bestConfigArima), 
                                                   self.__GenerateExpSmoothingModel(train, bestConfigETS)])
        
        # choose best model
        if bestModelType == const.ARIMA_MODEL:
            self.__Model = self.__GenerateArimaModel(self.__DataFrame, bestConfigArima)
        else:
            self.__Model = self.__GenerateExpSmoothingModel(self.__DataFrame, bestConfigETS)
        
    def SaveModel(self, path, name):
        if self.__Model is None:
            raise ValueError("Model not loaded")
        if not os.path.isdir(path):
            raise ValueError("Path must be a directory")
        
        if "/" in name or "." in name:
            raise ValueError("Name must not contain '/' or '.'")
        
        joblib.dump(self.__Model, path + name + ".pkl")
        
    def LoadModel(self, path):
        if path.endswith(".pkl") == False:
            raise ValueError("Please provide a pkl file")
        
        self.__Model = joblib.load(path)
        
    def GetModel(self):
        if self.__Model is None:
            raise ValueError("Model not loaded")
        
        return self.__Model
    
    def SetModel(self, model):
        if not isinstance(model, pmdarima.arima.ARIMA) and not isinstance(model, result.HoltWintersResultsWrapper):
            raise ValueError("Must be an Machine Learning model")

        self.__Model = model
        
    def Forecast(self, number, mode=const.DATE_MODE):
        if self.__DataFrame is None:
            raise ValueError("Dataframe not loaded")
        
        if self.__Model is None:
            raise ValueError("Model not loaded")
        
        if mode != const.DATE_MODE and mode != const.QUARTER_MODE:
            raise ValueError("Mode must be 'date' or 'quarter'")
        
        if isinstance(self.__Model, pmdarima.arima.ARIMA):
            predSeries = self.__Model.predict(n_periods=number)
        else:
            predSeries= self.__Model.forecast(number)
            
        predDF = pd.DataFrame({"Date": predSeries.index, "NOPAT": predSeries.values})
            
        if mode == const.QUARTER_MODE:
            predDF["Date"] = predDF["Date"].dt.to_period('Q').dt.strftime('Q%q/%Y')
        
        return predDF