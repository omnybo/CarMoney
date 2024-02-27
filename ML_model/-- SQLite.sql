-- SQLite
--Create CSV:
--SELECT 
--Car.Finnkode, Car.car_name, Car.Price, Spesifikasjoner.Specifications, Utstyr.Equipment
--FROM Car 
--LEFT JOIN Spesifikasjoner ON Car.Finnkode = Spesifikasjoner.Finnkode
--LEFT JOIN Utstyr ON Car.Finnkode = Utstyr.Finnkode
-- -- Find rows in Table2 that don't exist in Table1
-- This code deletes records from the "Spesifikasjoner" table that do not have a corresponding record in the "Car" table based on the "finnkode" column.
--DELETE FROM Spesifikasjoner
--WHERE finnkode IN (
--    SELECT Spesifikasjoner.finnkode
--    FROM Spesifikasjoner
--    LEFT JOIN Car ON Spesifikasjoner.finnkode = Car.finnkode
--    WHERE Car.finnkode IS NULL
--); --

SELECT * FROM Spesifikasjoner WHERE Specifications 