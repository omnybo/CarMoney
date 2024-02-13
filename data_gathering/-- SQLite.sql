-- SQLite
-- Create the Car table
CREATE TABLE IF NOT EXISTS Car (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Finnkode TEXT NOT NULL UNIQUE,
    car_name TEXT NOT NULL,
    Link TEXT NOT NULL,
    Price TEXT NOT NULL,
    Pictures TEXT,
    UNIQUE (Finnkode)
);

-- Create the Beskrivelse (Description) table
CREATE TABLE IF NOT EXISTS Beskrivelse (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Finnkode TEXT NOT NULL UNIQUE,
    Description_Text TEXT NOT NULL,
    FOREIGN KEY (Finnkode) REFERENCES Car (Finnkode)
);

-- Create the Spesifikasjoner (Specifications) table
CREATE TABLE IF NOT EXISTS Spesifikasjoner (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Finnkode TEXT NOT NULL UNIQUE,
    Specifications TEXT NOT NULL,
    FOREIGN KEY (Finnkode) REFERENCES Car (Finnkode)
);

-- Create the Utstyr (Equipment) table
CREATE TABLE IF NOT EXISTS Utstyr (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Finnkode TEXT NOT NULL UNIQUE,
    Equipment TEXT NOT NULL,
    FOREIGN KEY (Finnkode) REFERENCES Car (Finnkode)
);
