import pandas as pd
import json
import ast
import numpy as np
from matplotlib import pyplot as plt


def add_brand(df_cars):
    df = df_cars.copy()
    brands = ['AMC','Alfa Romeo', 'Alpina','Ariel','Aston Martin','Audi','Austin','BMW','BYD','Bentley','Buddy','Buick',
              'Cadillac','Chevrolet','Chrysler','Citroen','Cupra','DAF','DS','Dacia','Daewoo','Daihatsu','De Tomaso','Dodge',
              'Ferrari', 'Fiat', 'Fisker', 'Ford','GMC','Goupil','HiPhi','Honda', 'Hongqi','Hummer','Hyundai','Infiniti','Isuzu','Iveco',
              'JAC','Jaguar','Jeep','KGM','Kia','Lamborghini','Lancia','Land Rover','Lexus','Lincoln','Lotus',
              'MAN', 'MG','MINI', 'Maserati','Maxus','Maybach','Mazda','McLaren','Mercedes-Benz', 'Mercury',
              'Mitsubishi','Morgan','Morris','NIO','Nissan','Oldsmobile','Opel','Packard','Peugeot','Plymouth','Piaggio','Polestar','Pontiac','Porsche',
              'RAM','Radical','Renault','Rover','Rolls Royce','Saab','Seat','Seres','Skoda','Smart','Ssangyong','Subaru','Suzuki',
              'Tesla','TVR','Tazzari','Toyota','Triumph','Think', 'Volvo','VOYAH','Volkswagen','XPeng']
    
    for idx,row in df.iterrows():
        lowercase = row['car_name'].lower()
        brand_name = 'unknown'
        for brand in brands:
            if brand.lower() in lowercase:
                brand_name = brand
                break
        df.at[idx, 'brand'] = brand_name
    notknown = df[df['brand']=='unknown']
    print(notknown)
    print(len(notknown))
    return df

def clean_cars(df):
    df_cars = df.copy() 
    missing_values =  df_cars.isnull().sum()
    price_information = df_cars['Price'].describe()       
    df_cars.drop(df_cars.loc[df_cars['Price']>=5000000].index,inplace=True)
    return df_cars, price_information
def synchronize_dataframes(df_cars, df_utstyr, df_specs):

    # Extract the set of 'Finnkode' values that are present in base
    valid_finnkode_cars = set(df_cars['Finnkode'])
    valid_finnkode_utstyr = set(df_utstyr['Finnkode'])
    valid_finnkode_specs = set(df_specs['Finnkode'])

    valid_finnkode = valid_finnkode_cars.intersection(valid_finnkode_utstyr,valid_finnkode_specs)
    
    df_cars_synced = df_cars[df_cars['Finnkode'].isin(valid_finnkode)].copy()
    df_utstyr_synced = df_utstyr[df_utstyr['Finnkode'].isin(valid_finnkode)].copy()
    df_specs_synced = df_specs[df_specs['Finnkode'].isin(valid_finnkode)].copy()
    
    return df_cars_synced, df_utstyr_synced, df_specs_synced

if __name__ == "__main__":

    df_cars = pd.read_csv('full_dataset/all_cars.csv')
    df_specifications = pd.read_csv('full_dataset/all_specs.csv')
    df_equipment = pd.read_csv('full_dataset/all_equipments.csv')
    pd.options.display.float_format = '{:.2f}'.format  
    df_cars_processed, price_info = clean_cars(df_cars)
    print(f"Car Price Information: {price_info}")
    print("after", df_cars_processed['Price'].describe())
    '''
    #optionally: add brand name
    df_car = clean_cars(df_cars)
    df_car.rename(columns={"car_name": "name"},inplace=True)
    '''    
    
    df_cars_synced, df_specs_synced, df_equipment_synced = synchronize_dataframes(df_cars, df_equipment, df_specifications)

    #df_cars_synced.to_csv('../data/synced_cars.csv')
    #df_specs_synced.to_csv('../data/synced_specifications.csv')
    #df_equipment_synced.to_csv('../data/synced_equipment.csv')