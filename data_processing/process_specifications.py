from xml.etree.ElementInclude import include
import pandas as pd
import json
import ast
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
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

def correct_dtypes(df):
    df_specs = df.copy()
    cols_drop_units = ['Kilometer', 'Vekt', 'Maksimal tilhengervekt', 'CO2-utslipp','Omregistrering','Sylindervolum','Rekkevidde (WLTP)']
    #Drop units and convert to float
    for column in cols_drop_units:
        df_specs[column] = pd.to_numeric(df_specs[column].astype(str).str.replace(r'\D+', '', regex=True), errors='coerce')

    # Convert to integer with NaN handling
    columns_to_int = ['Antall eiere', 'Antall dører', 'Antall seter']
    for column in columns_to_int:
        # Use Int64 (capital "I") dtype for nullable integer support
        df_specs[column] = pd.to_numeric(df_specs[column], errors='coerce').astype('Int64')

    return df_specs

def clean_specifications(df):
    df_specs = df.copy()

    missing_per_row = df_specs.isna().sum(axis=1)
    missing_per_col = df_specs.isna().sum(axis=0)
    #print('missing vals:\n',missing_per_col,'\n')
    rows_to_drop = missing_per_row >= 18
    #print(f"Number of rows missing more than 18 values: {df_specs.isna().sum()}")
    df_specs = df_specs[~rows_to_drop]
    
    #Drop unnecessary columns and columns missing in more than 30k
    columns_to_drop = ['Bilen står i', 'Chassis nr. (VIN)', 'Årsavgift', 'Salgsform', 'Pris eks omreg','Fargebeskrivelse',
                       'Hjuldriftnavn','Garanti inntil','Batterikapasitet','Str. lasterom','Garanti']
    cleaned_specs = df_specs.drop(columns=columns_to_drop, axis=1)
    
    # Condition where 'Girkasse' is NaN and 'Drivstoff' is 'elektrisk'
    condition = (cleaned_specs['Girkasse'].isna()) & (cleaned_specs['Drivstoff'] == 'Elektrisitet')

    # Fill 'Girkasse' with 'Automat' under the specified condition
    cleaned_specs.loc[condition, 'Girkasse'] = 'Automat'
    #print(cleaned_specs[cleaned_specs['Rekkevidde (km)'].isna()][['Rekkevidde (km)', 'Finnkode', 'Drivstoff']])
    missing_per_cols = cleaned_specs.isna().sum(axis=0)
    #print('missing vals:\n',missing_per_cols,'\n')
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
    
    #condition = (df_filled['CO2-utslipp (g/km)'].isna()) & (df_filled['Drivstoff'] == 'Elektrisitet')
    #df_filled.loc[condition, 'CO2-utslipp (g/km)'] = 0


    return df_filled
def synchronize_dataframes(df1, df2):

    #Extract set of finnkode in the first dataframe
    valid_finnkode = set(df2['Finnkode'])

    # Retrieve rows with 'Finnkode' found in second dataframe
    df1_synced = df1[df1['Finnkode'].isin(valid_finnkode)].copy()
    
    # The cleaned_specs DataFrame is already cleaned and does not require further filtering based on df_cars
    df2_synced = df2.copy()
    
    # Return the synchronized DataFrames
    return df1_synced, df2_synced

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
    
    plt.show()


if __name__ == '__main__':
    df_cars = pd.read_csv('full_dataset/all_cars.csv')
    df_specifications = pd.read_csv('data/specifications_ready.csv')
    df_specifications.drop(columns='Unnamed: 0', axis=1, inplace=True)
    
    # correct datatypes from obj to int/float
    df_specifications = correct_dtypes(df_specifications)
    
    # Rename columns to include units
    df_specifications.rename(columns={"Maksimal tilhengervekt": "Maksimal tilhengervekt (kg)", "Vekt": "Vekt (kg)",
                                      "CO2-utslipp": "CO2-utslipp (g/km)", "Omregistrering": "Omregistrering (kr)", 
                                      "Sylindervolum": "Sylindervolum (liter)", "Rekkevidde (WLTP)": "Rekkevidde (km)"}, inplace=True)

    #clean
    cleaned = clean_specifications(df_specifications)
    
    # missing data
    missing_num_before, total_num_data_before = process_num_data(df_specifications)
    missing_num_after,total_num_data_after = process_num_data(cleaned)

    # show percent missing data per column
    avg_missing_data_before, percent_per_col_before = missing_numdata(df_specifications)
    avg_missing_data_after, percent_per_col_after = missing_numdata(cleaned)
    missing_numdata(cleaned)
    
    print(f"Percent missing values across dataset \n Before cleaning: {avg_missing_data_before}% \n After cleaning: {avg_missing_data_after}%")
    #plot_missing_data(percent_per_col_before, percent_per_col_after,'Original Data', 'Cleaned Data')
    
    #fill data:
    filled_data = fill_missing_values(cleaned)
    missing_values_filled, total_num_data_filled = process_num_data(filled_data)
    avg_missing_data_filled, percent_per_col_filled = missing_numdata(filled_data)
    #compare cleaned and with filled
    #plot_missing_data(percent_per_col_after, percent_per_col_filled, 'Cleaned Data', 'Data with Missing Values Filled In')
    
    #compare original and cleaned filled in data
    #plot_missing_data(percent_per_col_before, percent_per_col_filled, 'Raw data', 'Cleaned and filled data')
    
    missing_per_col = filled_data.isna().sum(axis=0)
    #print('missing vals filled:\n',missing_per_col,'\n')

    
    print(avg_missing_data_filled)

    #create df where all NaNs are filled in
    data_no_miss_vals = df_fill_all_data(cleaned)
    print(data_no_miss_vals.columns)


    #print(filled_data[filled_data['Drivstoff'].isna()][['Finnkode', 'Drivstoff', 'Kilometer']])

    #synchronize dataframes
    df_cars_synced, cleaned_specs_synced = synchronize_dataframes(df1=df_cars, df2=data_no_miss_vals)
    #merge based on id Finnkode
    #merged_df = pd.merge(df_cars_synced, cleaned_specs_synced, on='Finnkode', how='inner')
    '''
    #information
    
    print(df_specifications.info())
    print('\n')
    print(cleaned.info())
    '''