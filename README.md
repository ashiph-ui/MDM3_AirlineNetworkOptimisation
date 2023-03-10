# MDM3_AirlineNetworkOptimisation

**Flights.py Usage:**
```python
from Flights import Flights

easyjetFlights = Flights(airline="EZY")

easyjetFlights.df.head()
```
output:
```python
|   | aircraft_code | airline_iata | airline_icao | altitude | callsign | destination_airport_iata | ground_speed | heading | icao_24bit | id      | ... | origin_airport_iata | registration | squawk | time        | vertical_speed | get_altitude | get_flight_level | get_ground_speed | get_heading | get_vertical_speed |
|---|---------------|--------------|--------------|----------|----------|--------------------------|--------------|---------|------------|---------|-----|---------------------|--------------|--------|-------------|----------------|--------------|------------------|------------------|-------------|-------------------|
| 0 | A20N          | U2           | EZY          | 16975    | EZY35NT  | TFS                      | 369          | 196     | 407959     | 2f7953a7 | ... | EDI                 | G-UZLK       | N/A    | 1678469797 | -3584          | 16975 ft     | 169 FL           | 369 kts          | 196°        | -3584 fpm         |
| 1 | A20N          | U2           | EZY          | 37000    | EZY83BZ  | HRG                      | 452          | 136     | 4072C7     | 2f7954db | ... | MAN                 | G-UZHA       | N/A    | 1678469790 | 0              | 37000 ft     | 370 FL           | 452 kts          | 136°        | 0 fpm             |
| 2 | A320          | U2           | EZY          | 6825     | EZY52QV  | TFS                      | 255          | 176     | 40666C     | 2f795807 | ... | MAN                 | G-EZUS       | N/A    | 1678469797 | -576           | 6825 ft      | 6825 ft          | 255 kts          | 176°        | -576 fpm          |
| 3 | A320          | U2           | EZY          | 35025    | EJU96HM  | BER                      | 448          | 51      | 4408C9     | 2f795950 | ... | TFS                 | OE-IJU       | N/A    | 1678469794 | -64            | 35025 ft     | 350 FL           | 448 kts          | 51°         | -64 fpm           |
| 4 | A320          | U2           | EZY          | 35050    | EJU5584  | BER                      | 466          | 50      | 440395     | 2f796926 | ... | FNC                 | OE-IZO       | N/A    | 1678469797 | 64             | 35050 ft     | 350 FL           | 466 kts          | 50°         | 64 fpm            |
```
