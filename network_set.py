from FlightRadar24.api import FlightRadar24API
import pandas as pd
import datetime


from FlightRadar24.api import FlightRadar24API
import pandas as pd
import inspect

class Flights(FlightRadar24API):
    
    def __init__(self, airline="all", airport="all"):
        super(Flights).__init__()
        self.airline=airline
        self.airport=airport

        self.airline_flights = self.get_flights() if self.airline=="all" else self.get_flights(airline=self.airline)

        self.details = [self.get_flight_details(flight.id) for flight in self.airline_flights]

        for flight, detail in zip(self.airline_flights, self.details):
            try:
                flight.set_flight_details(detail)
            except:
                pass

        flight0 = self.airline_flights[-1]
        self.attrs = [attr for attr in dir(flight0) if (not attr.startswith("_")) and (type(getattr(flight0, attr)).__name__ != "method")]
        self.methods = [method for method in dir(flight0) if (type(getattr(flight0, method)).__name__ == "method")]
        self.others = [other for other in dir(flight0) if (other not in self.attrs) and (other not in self.methods)]
        self.attr_data = [(attr, val) for attr, val in zip(self.attrs, [getattr(flight0, attr) for attr in self.attrs])]

        ds = []
        for flight in self.airline_flights:

            attr_data = [(attr, val) for attr, val in zip(self.attrs, [getattr(flight, attr) for attr in self.attrs])]

            args = [[param for param in sig.parameters.values()] for sig in [inspect.signature(getattr(flight, method)) for method in self.methods]]
            methods_w_data = [self.methods[i] for i in range(len(self.methods)) if len(args[i]) == 0 and not self.methods[i].startswith("_")]
            methods_data = [(method, val) for method, val in zip(methods_w_data, [getattr(flight, method)() for method in methods_w_data])]
            
            ds.append(dict(attr_data+methods_data))
        
        self.df = pd.DataFrame(ds)


    def refresh(self):
        ds = []
        for flight in self.airline_flights:
            attr_data = [(attr, val) for attr, val in zip(self.attrs, [getattr(flight, attr) for attr in self.attrs])]

            args = [[param for param in sig.parameters.values()] for sig in [inspect.signature(getattr(flight, method)) for method in self.methods]]
            methods_w_data = [self.methods[i] for i in range(len(self.methods)) if len(args[i]) == 0 and not self.methods[i].startswith("_")]
            methods_data = [(method, val) for method, val in zip(methods_w_data, [getattr(flight, method)() for method in methods_w_data])]
            
            ds.append(dict(attr_data+methods_data))
        
        self.df = pd.DataFrame(ds)
        return self.df
    
    def to_csv(self, path):
        self.df.to_csv(path)
        
    
easyjet = Flights(airline="EZY", airport="LGW")
easyjet.to_csv("./easyjet.csv")
