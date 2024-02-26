-- SQLite
--Create CSV:
SELECT 
Car.Finnkode, Car.car_name, Car.Price, Spesifikasjoner.Specifications, Utstyr.Equipment
FROM Car 
LEFT JOIN Spesifikasjoner ON Car.Finnkode = Spesifikasjoner.Finnkode
LEFT JOIN Utstyr ON Car.Finnkode = Utstyr.Finnkode