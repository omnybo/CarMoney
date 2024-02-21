import sqlite3

def create_connection(database):
    try:
        connection = sqlite3.connect(database)
        print(f"SQLite version: {sqlite3.version}")
        return connection
    except sqlite3.Error as e:
        print(e)

def create_tables(connection):
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Car (Finnkode TEXT PRIMARY KEY,
                car_name TEXT NOT NULL,
                Link TEXT NOT NULL,
                Price REAL,
                Pictures TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Beskrivelse (Finnkode TEXT PRIMARY KEY,
                Description_Text TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Spesifikasjoner (Finnkode TEXT PRIMARY KEY,
                Specifications TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Utstyr (Finnkode TEXT PRIMARY KEY,
                Equipment TEXT)''')

    # Commit the changes
    connection.commit()   
def main():
    database_path = "../CARMONEY/data_gathering/cars_database.db"
    connection = create_connection(database_path)
    
    if connection is not None:
        create_tables(connection)
        
        connection.close()
        print('completed')
    print('completed')
if __name__ == "__main__":
    main()