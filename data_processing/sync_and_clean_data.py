import pandas as pd
import json
import ast
import numpy as np
import re

def safe_literal_eval(s):
    try:
        # Only attempt to evaluate strings that look like lists
        if isinstance(s, str) and s.startswith('[') and s.endswith(']'):
            return ast.literal_eval(s)
        # Return an empty list for empty strings or strings that don't look like lists
        return []
    except ValueError:
        # In case of any other unexpected ValueError, return an empty list as well
        return []

def safe_json_loads(string):
    try:
        return json.loads(string)
    except ValueError as e:
        print(f"Error loading JSON string: {e}")
        return {}


def create_specifications_df():
    df_spesifikasjoner = pd.read_csv('../data/new_specs_40k.csv')

    #access specifications column and convert JSON strings from csv file to Python dictionary
    df_spesifikasjoner['Specifications'] = df_spesifikasjoner['Specifications'].apply(json.loads)
    #Access the labels for each spec
    keys = list(df_spesifikasjoner['Specifications'].iloc[0].keys())
    # Create new columns for each key
    for key in keys:
        df_spesifikasjoner[key] = df_spesifikasjoner['Specifications'].apply(lambda x: x.get(key))
    #Create df copy to drop
    df_specs = df_spesifikasjoner.copy()
    df_specs = df_specs.drop(['Specifications'], axis=1)
    
    
    return df_specs
    
def clean_specifications(df):
    #minimize datatype
    df_specs = df.copy()
    
    #--Cleaning Kilometer --
    #remove string from 'Kilometer'
    df_specs['Kilometer'] = pd.to_numeric(df_specs['Kilometer'].str.replace(r'\D+', '', regex=True), errors='coerce')
    df_specs['Omregistrering'] = pd.to_numeric(df_specs['Omregistrering'].str.replace(r'\D+', '', regex=True), errors='coerce')
    df_specs['Finnkode'] = df_specs['Finnkode'].astype('int32')
    #fill none values across all columns with -1:
    
    df_specs.loc[:,'Kilometer'].fillna(-1)
    df_specs['Kilometer'] = df_specs['Kilometer'].astype('float32')
    
    df_specs.loc[:,'Omregistrering'].fillna(-1)
    df_specs['Omregistrering'] = df_specs['Omregistrering'].astype('float32')
    #convert columns to int dtype:
    
    columns_to_int = ['Modellår', 'Antall eiere', 'Antall dører']
    for column in columns_to_int:
        df_specs[column] = pd.to_numeric(df_specs[column], errors='coerce').fillna(-1).astype(int)
    
    columns_to_drop = ['Bilen står i', 'Chassis nr. (VIN)', 'Årsavgift', 'Salgsform']
    cleaned_specs = df_specs.drop(columns=columns_to_drop, axis=1)
    

    return cleaned_specs
  

def synchronize_dataframes(df_cars, cleaned_specs):
    # Ensure 'Finnkode' in cleaned_specs is the basis for synchronization
    # No need to clean df_cars as mentioned
    
    # Extract the set of 'Finnkode' values that are present in the cleaned specifications
    valid_finnkode = set(cleaned_specs['Finnkode'])

    # Filter the cars DataFrame to include only rows with 'Finnkode' found in the cleaned specifications
    df_cars_synced = df_cars[df_cars['Finnkode'].isin(valid_finnkode)].copy()
    
    # The cleaned_specs DataFrame is already cleaned and does not require further filtering based on df_cars
    cleaned_specs_synced = cleaned_specs.copy()
    
    # Return the synchronized DataFrames
    return df_cars_synced, cleaned_specs_synced


def split_drivstoff(df):
    pass

def print_information(path):
    df = pd.read_csv(path)
    

if __name__ == "__main__":
    
    df_full_specs = pd.read_csv('../data/new_specs_40k.csv')
    df_cars = pd.read_csv('../data/new_cars_40k.csv')

    specifications  = create_specifications_df()
    num_missing_per_row = specifications.isna().sum(axis=1)
    
    # Identify rows with 9 or more missing values
    rows_with_many_missing = num_missing_per_row >= 9
    
    # Drop these rows
    specifications_reduced = specifications[~rows_with_many_missing]
    
    print(f"Original number of rows: {len(specifications)}")
    print(f"Number of rows after dropping rows with 9 or more missing values: {len(specifications_reduced)}") #specs_copy = specifications.copy()
    
    cleaned_specifications = clean_specifications(specifications_reduced)
    #print(cleaned_specifications['Omregistrering'])
    
    cleaned_specifications.to_csv('../data/cleanednew.csv')
    

    #incomplete_info = specifications.isna().sum()
    #print(f"Rows missing more than 3 values: \n {incomplete_info}")
  
    #nan_count = specifications_clean.isna().sum()
    #print(f"Missing values: \n {nan_count}")  


    #Rows containing all information
    #complete_carspecifications = specifications_clean.notna().all(axis=1).sum()
    #print(f"Cars containing all specifications: \n {complete_carspecifications} \n")

    
    #print(complete_cars)
    #df_cars_synced, full_specs_synced = synchronize_dataframes(df_cars, car_specs_filled)
 
    #df_cars_synced.to_csv('../data_processing/cleaned_cars_40k.csv')
    #full_specs_synced.to_csv('../data_processing/cleaned_specifications_40k.csv')
