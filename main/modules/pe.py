import main.common.const as const

class PEHelper:
    """
    This helper is used to forecast stock prices for a year based on quarterly data, using the PE method. 
    Example: To forecast stock price for the year 2023, you require the quarterly data for all four quarters of that year.
    """
    def __init__(self, rate=0.75, unit=10**9):
        self.AdjustmentRate = rate
        self.Unit = unit
        
    def CountDataPoints(self, values):
        return len(values) // 4
    
    def GetDataPoints(self, values, number, mode=const.END_MODE):
        if mode != const.START_MODE and mode != const.END_MODE:
            raise ValueError("Mode must be 'START' or 'END'")
        
        if number <= 0:
            raise ValueError("Number must be greater than 0")
        
        if number > self.CountDataPoints(values):
            raise ValueError("Not enough data points")
        
        if mode == const.END_MODE:
            return values[-(4 * number):]
        else:
            return values[:(4 * number)]
        
    def CalPATByYear(self, listPAT):
        if len(listPAT) % 4 != 0:
            raise ValueError("Need enough data for 4 quarters to calculate")
        
        listYearPAT = []
        
        for i in range(0, len(listPAT), 4):
            listYearPAT.append(sum(listPAT[i:i+4]) * self.Unit)
            
        return listYearPAT

    def CalEPSByYear(self, listPAT, sharesOutstanding):
        listYearPAT = self.CalPATByYear(listPAT)
        listYearEPS = []
        
        for i in listYearPAT:
            listYearEPS.append(i / sharesOutstanding)
            
        return listYearEPS
    
    def ForecastStockPrices(self, listPAT, sharesOutstanding, peForecasted):
        listYearEPS = self.CalEPSByYear(listPAT, sharesOutstanding)
        listStockPrices = []
        
        for i in listYearEPS:
            listStockPrices.append(i * peForecasted * self.AdjustmentRate)
            
        return listStockPrices