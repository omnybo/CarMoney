import pandas as pd


def split_el_cars():
    # Load dataset
    data = pd.read_csv('cars_data/cars_withbrand_train.csv')

    # Filter rows where 'Drivstoff' = 'Elektrisk'
    electric_cars = data[data['Drivstoff'] == 'Elektrisitet']
    electric_cars.drop(['Sylindervolum', 'CO2Utslipp'], axis=1, inplace=True)

    # Finf rows where 'Drivstoff' is not = 'Elektrisk'
    non_electric_cars = data[data['Drivstoff'] != 'Elektrisitet']
    non_electric_cars.drop(['Rekkevidde'], axis=1, inplace=True)

    # Saving the new datasets
    electric_cars.to_csv('cars_data/electric_cars.csv', index=False)
    non_electric_cars.to_csv('cars_data/non_electric_cars.csv', index=False)
