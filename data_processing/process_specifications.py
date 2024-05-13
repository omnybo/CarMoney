import pandas as pd
import json
import ast
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
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
    #Create dataframe, set dictionary keys as columns
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

def correct_dtypes(df, cols_drop_units):
    df_specs = df.copy()

    #drop units in across columns
    for column in cols_drop_units:
        if column in df.columns:
            print(f"Data for {column} before cleaning {df_specs[column].unique()[:5]}  ")  # Display first 5 unique cleaned values

            #Assuming decimals are not important except for specific fields like 'Vekt'
            regex_pattern = r'[^\d.]'
            df_specs[column] = pd.to_numeric(df_specs[column].astype(str).str.replace(regex_pattern, '', regex=True), errors='coerce') 
            print(f"Cleaned data for {column}: {df_specs[column].unique()[:5]}")  # Display first 5 unique cleaned values
   
    #Convert columns to dtype integer
    columns_to_int = ['Antall eiere', 'Antall dører', 'Antall seter']
    for column in columns_to_int:
        if column in df_specs.columns:
            df_specs[column] = pd.to_numeric(df_specs[column], errors='coerce').astype('Int64')

    return df_specs

def clean_specifications(df, thresh_decimal):
    df_specs = df.copy()

    missing_per_row = df_specs.isna().sum(axis=1)
    missing_per_col = df_specs.isna().sum(axis=0)
    print('Missing Before:\n',missing_per_col,'\n')
    #drop rows missing more than x percent values
    rows_to_drop = missing_per_row >= len(df_specs.columns.isna())*thresh_decimal
    print(f"Number of rows: {df_specs.isna().sum()}")
    df_specs = df_specs[~rows_to_drop]
    
    #Dropping unnecessary columns and columns missing in more than 30k
    columns_to_drop = ['Bilen står i', 'Chassis nr. (VIN)', 'Årsavgift', 'Salgsform', 'Pris eks omreg','Fargebeskrivelse',
                       'Hjuldriftnavn','Garanti inntil','Batterikapasitet','Str. lasterom','Garanti']
    cleaned_specs = df_specs.drop(columns=columns_to_drop, axis=1)
    
    #fill with 'Automat' if condition is met
    condition = (cleaned_specs['Girkasse'].isna()) & ((cleaned_specs['Drivstoff'] == 'Elektrisitet') |(cleaned_specs['Drivstoff'] == 'El + Bensin') | (cleaned_specs['Drivstoff'] == 'El + Diesel'))
    cleaned_specs.loc[condition, 'Girkasse'] = 'Automat'

    return cleaned_specs

def fill_missing_values(df):
    df_filled = df.copy()
    #fill missing values
    int_col_to_fill = ['Antall seter','Antall dører', 'Sylindervolum (liter)','Kilometer',
                       'Omregistrering (kr)','Antall eiere','Rekkevidde (km)']
    df_filled[int_col_to_fill] = df_filled[int_col_to_fill].fillna(-1)

    #fill with 'zero' for missing values on object columns
    obj_col_to_fill = ['Farge','Interiørfarge','Girkasse','Sist EU-godkjent','Vedlikehold']

    df_filled[obj_col_to_fill] = df_filled[obj_col_to_fill].fillna('zero')
    

    return df_filled

def process_num_data(df):
    float64_data = df.select_dtypes(include=['float64'])
    int_data = df.select_dtypes(include=['int32', 'int64'])
    total_num_data = df.select_dtypes(include=['int32', 'int64','float64'])
    # compute missing data per dtype
    missing_float_data = float64_data.isna().sum().sum()
    missing_int_data = int_data.isna().sum().sum()
    total_num_missing = missing_float_data+missing_int_data
    print(f"Missing numeric data:integer data: {missing_int_data} \n float64: {missing_float_data} \n total: {total_num_missing}")

    return total_num_missing, total_num_data

def missing_numdata(df):
    
    all_data = len(df)
    percent_missing_per_column = (df.isnull().sum()/all_data )*100
    
    avg_missing_percent = percent_missing_per_column.mean()
 
    return avg_missing_percent, percent_missing_per_column

def process_cat_data(df):
    categorical_data = df.select_dtypes(include=['object'])
    missing_cat_data = categorical_data.isna().sum().sum()
    print('Missing data in cat_cols:', missing_cat_data)

def df_fill_all_data(df):
    df_filled_all = df.copy()

    int_cols =  df_filled_all.select_dtypes(include = ['int32','int64']).columns
    float_cols = df_filled_all.select_dtypes(include = ['float64']).columns
    obj_cols = df_filled_all.select_dtypes(include= ['object']).columns

    df_filled_all[obj_cols] = df_filled_all[obj_cols].fillna('zero')
    df_filled_all[int_cols] = df_filled_all[int_cols].fillna(-1)
    df_filled_all[float_cols] = df_filled_all[float_cols].fillna(-1)

    return df_filled_all
def plot_missing_data(percent_missing_before, percent_missing_after, datalabel1, datalabel2):
    # Convert the Series to a DataFrame for plotting
    missing_data_df = percent_missing_before.reset_index()
    missing_data_df.columns = ['Feature', 'Missing Percentage']
    
    missing_data_df_after = percent_missing_after.reset_index()
    missing_data_df_after.columns = ['Feature', 'Missing Percentage']
    
    merged = pd.merge(missing_data_df,missing_data_df_after, on='Feature')
    combined_melt = merged.melt(id_vars='Feature', var_name='Cleaning State', value_name='Missing Percentage')
    # Sort the DataFrame by the Missing Percentage
    missing_data_df = missing_data_df.sort_values(by='Missing Percentage', ascending=False)
    
    plt.figure(figsize=(15, 10))  # Increase figure size
    sns.barplot(x='Missing Percentage', y='Feature', hue='Cleaning State', data=combined_melt, palette='viridis')

    plt.title('Comparison of Missing Data Percentage Before and After Cleaning', fontsize=16)
    plt.xlabel('Percentage of Missing Data', fontsize=14)
    plt.ylabel('Feature', fontsize=14)

    plt.xticks(rotation=90, fontsize=12)  # Rotate labels and adjust font size if needed
    legend_labels = [datalabel1,datalabel2]
    legend_handles, _ = plt.gca().get_legend_handles_labels()
    for handle, label in zip(legend_handles, legend_labels):
        handle.set_y(0.4)
        handle.set_picker(True)
        handle.set_label(label)
    plt.gca().legend(title="Cleaning State")
    plt.tight_layout()
    plt.savefig('dataComparison')
  
def plot_hist(df,column,title,x_label, y_label,xbins):
    plt.figure(figsize=(10, 6))

    bins = [xbins]
    plt.hist(x=df[column], bins=xbins, color='skyblue', edgecolor='gray')  
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    #plt.show()

if __name__ == '__main__':
    #df_cars = pd.read_csv('full_dataset/all_cars.csv')
    df_specifications = pd.read_csv('data_processing/specifications_ready.csv')
    df_specifications.drop(columns='Unnamed: 0', axis=1, inplace=True)
    df_specifications.rename(columns={"Maksimal tilhengervekt": "Maksimal tilhengervekt (kg)", "Vekt": "Vekt (kg)",
                                      "CO2-utslipp": "CO2-utslipp (g/km)", "Omregistrering": "Omregistrering (kr)", 
                                      "Sylindervolum": "Sylindervolum (liter)", "Rekkevidde (WLTP)": "Rekkevidde (km)", "Effekt": "Effekt (hk)"}, inplace=True)
    missing = df_specifications.isnull().sum().sum()
    #print(missing.sort_values(ascending=True))
    print(f"\n Total missing values:\n {missing}\n")
    print(f"Rows, Columns: [{df_specifications.shape[0]},{df_specifications.shape[1]}]")
    
    columns_to_drop_units = ['Kilometer','Effekt (hk)', 'Vekt (kg)', 'Maksimal tilhengervekt (kg)', 'CO2-utslipp (g/km)','Omregistrering (kr)','Sylindervolum (liter)','Rekkevidde (km)']
    # correct datatypes from obj to int/float
    df_specs = correct_dtypes(df_specifications, columns_to_drop_units)
    missing_per_row = df_specs.isna().sum(axis=1)
    missing_per_col = df_specs.isna().sum(axis=0)
   
    cleaned = clean_specifications(df_specs)
    cleaned.to_csv('cleaned_data.csv')
    nans = pd.DataFrame(cleaned.isnull().sum().sort_values(ascending=False), columns=['Number of missing values'])
    #missing values percent
    nans['% Missing'] = cleaned.isnull().sum().sort_values(ascending=False)/len(cleaned)
    print(nans)

    missing_num_before, total_num_data_before = process_num_data(df_specifications)
    missing_num_after, total_num_data_after = process_num_data(cleaned)
    print(f"Numeric data integrity, before vs. after cleaning: \n Before: {missing_num_before} missing \n After: {missing_num_after} missing")

    #percent missing data per column
    avg_missing_data_before, percent_per_col_before = missing_numdata(df_specifications)
    avg_missing_data_after, percent_per_col_after = missing_numdata(cleaned)
    
    print(f"Percent missing values across dataset \n Before cleaning: {avg_missing_data_before}% \n After cleaning: {avg_missing_data_after}%")
    plot_missing_data(percent_per_col_before, percent_per_col_after,'Original Data', 'Cleaned Data')
    
    #fill data:
    filled_data = fill_missing_values(cleaned)
    missing_values_filled, total_num_data_filled = process_num_data(filled_data)
    avg_missing_data_filled, percent_per_col_filled = missing_numdata(filled_data)

    #compare original and cleaned filled in data
    plot_missing_data(percent_per_col_before, percent_per_col_filled, 'Raw data', 'Cleaned and filled data')
    
    missing_per_col = filled_data.isna().sum(axis=0)
    print('missing vals filled:\n',missing_per_col,'\n')

    print(avg_missing_data_filled)
