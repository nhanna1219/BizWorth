import numpy_financial as npf
import main.common.const as const

class Mx4Helper:
    """
    This helper is used to caculate the 4M score for a year, using data from the 5 nearest years and the data for that specific year.
    Example: To calculate the 4M score for 2022, you need data spanning from 2017 to 2022.
    """
    def __init__(self, weights=[0.3,0.4,0.3], reference=[0.2,0.2,0.15,0.15,0.1,0.15,0.2,0.15,3], proportions=[0.15,0.2,0.05,0.15,0.05,0.1,0.05,0.15,0.1]):
        if len(weights) != 3 and sum(weights) != 1:
            raise ValueError("Weights must be a list of 3 numbers, and sum to 1")
        
        if len(reference) != 9:
            raise ValueError("Reference must be a list of 9 numbers")
        
        if len(proportions) != 9 and sum(proportions) != 1:
            raise ValueError("Proportions must be a list of 9 numbers, and sum to 1")
        
        self.Weights = weights
        self.ReferenceRates = reference
        self.Proportions = proportions
        
    def __CalRate(self, present, past, period):        
        return npf.rate(period, 0,-past, present)
    
    def __CalScore(self, values, index):
        if len(values) != 3:
            raise ValueError("Values must be a list of 3 numbers")
        
        score = 0
        
        for i, value in enumerate(values):
            if value >= self.ReferenceRates[index]:
                score += self.Weights[i]
            else:
                result = round((value / self.ReferenceRates[index]) * self.Weights[i],4)
                
                if result < 0:
                    result = 0
                    
                score += result
                
        return score * 100
    
    def __CalSum(self, scores):
        if len(scores) != 9:
            raise ValueError("Scores must be a list of 9 numbers")
        
        return sum(map(lambda x, y: x * y, scores, self.Proportions))
    
    def __Cal4MScore(self, table):
        if len(table) != 9:
            raise ValueError("table must be a list of 9 numbers")
        
        scores = []
        
        for i in range(8):
            if len(table[i]) != 3:
                raise ValueError(f"table [{i}] must be a list of 9 lists of 3 numbers")
            scores.append(self.__CalScore(table[i], i))
            
        if len(table[8]) != 2:
            raise ValueError("table [8] must be a list of 2 number")
        
        if table[8][0] < (table[8][1] * self.ReferenceRates[8] * 1e3):
            scores.append(100)
        else:
            scores.append(0)
        
        return self.__CalSum(scores)
    
    def __GenerateList(self, data):
        if len(data) != 4:
            raise ValueError("data must be a list of 4 numbers")
        
        return [self.__CalRate(data[3], data[2], 1), self.__CalRate(data[3], data[1], 3), self.__CalRate(data[3], data[0], 5)]
    
    def __GenerateTable(self, data, mode=const.EFFECTIVENESS_MODE):
        if not isinstance(data, Data4M):
            raise ValueError("data must be a class Data4M")

        if not data.Map_Check(lambda x: len(x) == 4):
            raise ValueError("data must be a class Data4M with 4 elements in each list")
        
        if not mode in [const.EFFECTIVENESS_MODE, const.EFFCIENCY_MODE, const.PRODUCTITIVTY_MODE]:
            raise ValueError("mode must be EFFECTIVENESS_MODE, EFFCIENCY_MODE, or PRODUCTITIVTY_MODE")
        
        sales = self.__GenerateList(data.Sales)
        eps = self.__GenerateList(data.EPS)
        bvps = self.__GenerateList(data.BVPS)
        opc = self.__GenerateList(data.OPC)
        
        if mode == const.EFFECTIVENESS_MODE:
            mode_data = self.__GenerateList(list(map(lambda x, y: x / y, data.Sales, data.Assets)))
        elif mode == const.EFFCIENCY_MODE:
            mode_data = self.__GenerateList(list(map(lambda x, y: x / y, data.PAT, data.Sales)))
        else:
            mode_data = self.__GenerateList(list(map(lambda x, y: x / y, data.OPC, data.PAT)))
            
        roa = self.__GenerateList(list(map(lambda x, y: x / y, data.PAT, data.Assets)))
        roe = self.__GenerateList(list(map(lambda x, y: x / y, data.PAT, data.Equity)))
        roic = self.__GenerateList(list(map(lambda x, y, z: x / (y + z), data.PAT, data.Equity, data.LongDebt)))
        nearestLongDebt = [data.LongDebt[2], data.PAT[2]]
        
        return [sales, eps, bvps, opc, mode_data, roa, roe, roic, nearestLongDebt]
    
    def CountDataPoints(self, data):
        if not isinstance(data, Data4M):
            raise ValueError("data must be a class Data4M")
        
        if data.Map_Check(lambda x: len(x) < 6):
            return 0
        else:
            return len(data.Sales) - 5
    
    def GetDataPoints(self, data, number, mode=const.END_MODE):
        if mode != const.START_MODE and mode != const.END_MODE:
            raise ValueError("Mode must be 'START' or 'END'")
        
        if number < 0:
            raise ValueError("Number must be positive")
        
        if number > self.CountDataPoints(data):
            raise ValueError("Not enough data points")

        if mode == const.END_MODE:
            data.Map(lambda x: x[-(5 + number):])
        else:
            data.Map(lambda x: x[:(5 + number)])
            
        return data
    
    def Evaluate4MScore(self, score):
        if score < 0 or score > 100:
            raise ValueError("Score must be between 0 and 100")

        if score > 79:
            return const.GOOD_SCORE
        elif score > 59:
            return const.MEDIUM_SCORE
        elif score > 19:
            return const.BAD_SCORE
        else:
            return const.VERYBAD_SCORE
        
    def CalList4MScores(self, data, mode=const.EFFECTIVENESS_MODE):
        numb = self.CountDataPoints(data)
        list4MScores = []
        
        if numb == 0:
            return list4MScores
        else:
            listTables = []
            
            for index in range(numb):
                listTables.append(self.__GenerateTable(data.Map_Return(lambda x: [x[index], x[index + 2], x[index + 4], x[index + 5]]), mode))
                
            for table in listTables:
                list4MScores.append(self.__Cal4MScore(table))
                
            return list4MScores
                
    
class Data4M:
    def __init__(self, sales, eps, bvps, opc, longDebt, pat, assets, equity):
        length = len(sales) + len(eps) + len(bvps) + len(opc) + len(longDebt) + len(pat) + len(assets) + len(equity)
        
        if length % 8 != 0:
            raise ValueError("All arguments must be the same length")
        
        self.Sales = sales
        self.EPS = eps
        self.BVPS = bvps
        self.OPC = opc
        self.LongDebt = longDebt
        self.PAT = pat
        self.Assets = assets
        self.Equity = equity
        
    def Get(self):
        return [self.Sales, self.EPS, self.BVPS, self.OPC, self.LongDebt, self.PAT, self.Assets, self.Equity]
        
    def Map(self, fc):
        if not callable(fc):
            raise ValueError("fc must be a function")
        
        for key in self.__dict__:
            self.__dict__[key] = fc(self.__dict__[key])
            
    def Map_Return(self, fc):
        if not callable(fc):
            raise ValueError("fc must be a function")
        
        new = Data4M([], [], [], [], [], [], [], [])
        
        for key in self.__dict__:
            new.__dict__[key] = fc(self.__dict__[key])
            
        return new
            
    def Map_Check(self, fc):
        if not callable(fc):
            raise ValueError("fc must be a function")
        
        for key in self.__dict__:
            if not fc(self.__dict__[key]):
                return False
            
        return True