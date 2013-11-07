import Quandl

data = Quandl.get("GOOG/NYSE_IBM", frequency="daily")
data.head()
print data
