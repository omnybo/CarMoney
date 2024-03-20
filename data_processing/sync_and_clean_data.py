import pandas as pd
import json
import ast
import numpy as np



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

def create_specs_csv():

    filepath='full_dataset/all_specifications.csv'
    
    specifications  = create_specifications_df(filepath)
    specifications.to_csv('data_processing/specifications_ready.csv')

def create_specifications_df(filepath):
    
    df_spesifikasjoner = pd.read_csv(filepath)
    all_keys = set()

    for row in df_spesifikasjoner['Specifications']:
        spec_dict = json.loads(row)
        all_keys.update(spec_dict.keys())
    
    for key in all_keys:
        df_spesifikasjoner[key] = df_spesifikasjoner['Specifications'].apply(lambda x: json.loads(x).get(key, pd.NA))


    df_specs = df_spesifikasjoner.copy()
    df_specs = df_specs.drop(['Specifications'], axis=1)
    
    return df_specs

def clean_specifications(df):
    df_specs = df.copy()
       
    #Drop units in columns:
    cols_drop_units = ['Kilometer', 'Vekt (kg)', 'Maksimal tilhengervekt (kg)', 'CO2-utslipp (g/km)','Omregistrering (kr)']
    for column in cols_drop_units:
        df_specs[column] = pd.to_numeric(df_specs[column].astype(str).str.replace(r'\D+', '', regex=True), errors='coerce')
    
    #--Cleaning Kilometer --
    #remove string from 'Kilometer'
    print('before',df_specs['Kilometer'].isna().sum())
    #df_specs['Kilometer'] = pd.to_numeric(df_specs['Kilometer'].str.replace(r'\D+', '', regex=True), errors='coerce')
    df_specs['Kilometer'] = df_specs['Kilometer'].fillna(-1)
    df_specs['Kilometer'] = df_specs['Kilometer'].astype('float32')
        
    df_specs['Finnkode'] = df_specs['Finnkode'].astype('int32')
    #df_specs['Omregistrering'] = pd.to_numeric(df_specs['Omregistrering (kr)'].str.replace(r'\D+', '', regex=True), errors='coerce')
    df_specs['Omregistrering (kr)'] = df_specs['Omregistrering (kr)'].fillna(-1)
    df_specs['Omregistrering (kr)'] = df_specs['Omregistrering (kr)'].astype('float32')
    #convert columns to int dtype:
    

    df_specs['1. gang registrert'] =df_specs['1. gang registrert'].replace('01.01.0001', None)
    columns_to_drop = ['Bilen står i', 'Chassis nr. (VIN)', 'Årsavgift', 'Salgsform']
    cleaned_specs = df_specs.drop(columns=columns_to_drop, axis=1)
    print('after', cleaned_specs['Kilometer'].isna().sum())


    return cleaned_specs

def clean_dtypes(df_specs):
    columns_to_int = ['Modellår', 'Antall eiere', 'Antall dører','Antall seter']
    for column in columns_to_int:
        df_specs[column] = pd.to_numeric(df_specs[column], errors='coerce').fillna(-1).astype(int)
    
    return df_specs
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


if __name__ == "__main__":
    #Read and create specifications df:
    #create_specs_csv()

    df_cars = pd.read_csv('full_dataset/all_cars.csv')

    create_specs_csv()
    #rename columns for cleaning purposes
    df_specs = pd.read_csv('data_processing/specifications_ready.csv')
    df_specs.rename(columns={"Maksimal tilhengervekt":"Maksimal tilhengervekt (kg)", "Vekt":"Vekt (kg)",
                                    "CO2-utslipp":"CO2-utslipp (g/km)","Omregistrering":"Omregistrering (kr)"},inplace=True)
    
    num_missing_per_row = df_specs.isna().sum(axis=1)
    
    # Identify rows with 50% or more missing values
    '''
    rows_with_many_missing = num_missing_per_row >= 18
    
    # Drop these rows
    specifications_reduced = df_specs[~rows_with_many_missing]
    
    print(f"Original number of rows: {len(df_specs)}")
    print(f"Number of rows after dropping rows with 9 or more missing values: {len(specifications_reduced)}") #specs_copy = specifications.copy()
   
    cleaned_specifications = clean_specifications(specifications_reduced)

    #cleaned_specifications.to_csv('data/cleaned_new.csv')

    #synchronized cleaned specifications with cars:
    df_cars_synced, cleaned_specs_synced = synchronize_dataframes(df_cars=df_cars, cleaned_specs=cleaned_specifications)
    '''
    '''
    print(f"Cars after sync: \n {len(df_cars_synced)} \n Specifications after sync: \n {len(cleaned_specs_synced)}")
    missing_values_car = df_cars_synced.isna().sum(axis=1)
    print(f"cars miss: \n {missing_values_car} \n")
    missing_values_specifications = cleaned_specs_synced.isna().sum(axis=1)
    print(f"specs miss: \n {missing_values_specifications} \n")

    print(cleaned_specs_synced.isna().sum().sum())
    '''

'''  
    #Rows containing all information
    #complete_carspecifications = specifications_clean.notna().all(axis=1).sum()
    #print(f"Cars containing all specifications: \n {complete_carspecifications} \n")

    
    #print(complete_cars)
    #df_cars_synced, full_specs_synced = synchronize_dataframes(df_cars, car_specs_filled)
 
    #df_cars_synced.to_csv('../data_processing/cleaned_cars_40k.csv')
    #full_specs_synced.to_csv('../data_processing/cleaned_specifications_40k.csv')
    '''