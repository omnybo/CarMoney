-- SQLite
DELETE FROM Car WHERE car_name='Phyron Automated Video &The Phyron Video Player';


DELETE FROM Car WHERE Price ISNULL;

--DELETE FROM Car WHERE Finnkode ='342449056';

-- Delete entries in Spesifikasjoner with no match in Car
DELETE FROM Beskrivelse
WHERE Finnkode NOT IN (
    SELECT Finnkode FROM Car
);

-- Delete entries in Utstyr with no match in Car
DELETE FROM Utstyr
WHERE Finnkode NOT IN (
    SELECT Finnkode FROM Car
);


DELETE FROM Spesifikasjoner
WHERE Finnkode NOT IN (
   SELECT Finnkode FROM Car
);

DELETE FROM Car
WHERE Finnkode NOT IN(
  SELECT Finnkode FROM Spesifikasjoner
);
