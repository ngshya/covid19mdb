from numpy import array, exp, arange, max
from scipy.optimize import curve_fit


class ModelLogistic:

    def __init__(self):
        self.name = "Logistic"

    @staticmethod
    def __logistic(array_x, L, k, xm):
        array_x = array(array_x)
        return L / (1+exp(-k*(array_x-xm)))

    def fit(self, y):
        self.y = y
        self.X = arange(1, len(self.y)+1)
        self.optimal_params, _ = curve_fit(
            f=self.__logistic, 
            xdata=self.X, 
            ydata=self.y, 
            maxfev=10000, 
            p0=[max(self.y)+1, 1, 1])

    def forecast(self, n_forecast):
        self.array_steps_forecast = arange(1, len(self.y)+n_forecast+1)
        y = self.__logistic(
            L=self.optimal_params[0],
            k=self.optimal_params[1],
            xm=self.optimal_params[2],
            array_x=self.array_steps_forecast
        )
        self.y_forecast = y
        return {
            "past_fit": self.y_forecast[:len(self.y)], 
            "forecast": self.y_forecast[len(self.y):]
        }