from Flights import Flights        
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()

easyjet = Flights(airline="EZY", airport="LGW")
easyjet.df.to_csv(now.strftime("%Y-%m-%d_%H-%M-%S") + "_EZY_LGW.csv")
