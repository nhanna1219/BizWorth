import numpy_financial as npf
import main.common.const as const

class CanslimHelper:
    """
    This helper is used to caculate the CANSLIM score for a quarter, using data from the 8 nearest quarters and the data for that specific quarter.
    Example: To calculate the CANSLIM score for the third quarter of 2023, you need data spanning from the third quarter of 2023 to the third quarter of 2021.
    """
    def __init__(self, reference=[0.25,0.25,0.2,0.2,0.25,0.25,0.2,0.2], proportions=[0.15,0.1,0.1,0.05,0.2,0.15,0.15,0.1]):
        if len(reference) != 8:
            raise ValueError("Reference must be a list of 8 numbers")
        
        if len(proportions) != 8 and sum(proportions) != 1:
            raise ValueError("Proportions must be a list of 8 numbers, and sum to 1")
            
        self.ReferenceRates = reference
        self.Proportions = proportions
        
    def __CalQuarterRate(self, value):
        if len(value) != 2:
            raise ValueError("Value must be a list of 2 numbers")
        
        return npf.rate(1, 0,-value[0], value[1])
    
    def __CalTTMRate(self, value):
        if len(value) != 8:
            raise ValueError("Value must be a list of 8 numbers")
        return sum(value[4:8]) / sum(value[0:4]) - 1
        
    def __CalScore(self, value, index):        
        if value > self.ReferenceRates[index]:
            return self.Proportions[index] * 100
        else:
            result = round((value / self.ReferenceRates[index]) * self.Proportions[index], 4) * 100
            
            if result < 0:
                return 0
            
            return result
    
    def __GenerateTable(self, sales, eps):
        if len(sales) != 9 or len(eps) != 9:
            raise ValueError("Sales and EPS must be a list of 8 numbers")
        
        c1, e1 = [sales[4], sales[8]], [eps[4], eps[8]]
        c2, e2 = [sales[3], sales[7]], [eps[3], eps[7]]
        c3, e3 = sales[1:9], eps[1:9]
        c4, e4 = sales[0:8], eps[0:8]
        
        return [c1, c2, c3, c4, e1, e2, e3, e4]
    
    def __CalCanslimScore(self, table):
        if len(table) != 8:
            raise ValueError("Table must be a list of 8 numbers")
        
        if len(table[0]) != 2 or len(table[1]) !=2 or len(table[4]) != 2 or len(table[5]) != 2:
            raise ValueError("Table([0],[1],[4],[5]) must be a list of 2 numbers")
        
        if len(table[2]) != 8 or len(table[3]) != 8 or len(table[6]) != 8 or len(table[7]) != 8:
            raise ValueError("Table([2],[3],[6],[7]) must be a list of 8 numbers")
        
        sum = 0
        
        for index in range(4):
            if index < 2:
                sum += self.__CalScore(self.__CalQuarterRate(table[index]), index) + \
                       self.__CalScore(self.__CalQuarterRate(table[index + 4]), index + 4)
            else:
                sum += self.__CalScore(self.__CalTTMRate(table[index]), index) + \
                       self.__CalScore(self.__CalTTMRate(table[index + 4]), index + 4)
                       
        return sum
    
    def CountDataPoints(self, values):
        if len(values) < 9:
            return 0
        else:
            return len(values) - 8
        
    def GetDataPoints(self, values, number, mode=const.END_MODE):
        if mode != const.START_MODE and mode != const.END_MODE:
            raise ValueError("Mode must be 'START' or 'END'")
        
        if number < 0:
            raise ValueError("Number must be positive")
        
        if number > self.CountDataPoints(values):
            raise ValueError("Not enough data points")

        if mode == const.END_MODE:
            return values[-(8 + number):]
        else:
            return values[:(8 + number)]
        
    def EvaluateCanslimScore(self, score):
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
        
    def CalListCanslimScores(self, sales, eps):
        if len(sales) != len(eps):
            raise ValueError("Sales and EPS must be a list of same length")
        
        numb = self.CountDataPoints(sales)
        listCanslimScores = []
        
        if numb == 0:
            return listCanslimScores
        else:
            listTables = []
            
            for index in range(numb):
                listTables.append(self.__GenerateTable(sales[index:index + 9], eps[index:index + 9]))
                
            for table in listTables:
                listCanslimScores.append(self.__CalCanslimScore(table))
                
            return listCanslimScores