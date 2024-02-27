import pandas as pd
import json

     
def retrieve_data():
    df_cars = pd.read_csv('../data_processing/table_car.csv')
    df_spesifikasjoner = pd.read_csv('../data_processing/table_spesifikasjoner.csv')
    df_utstyr = pd.read_csv('../data_processing/table_utstyr.csv')
    df_beskrivelse = pd.read_csv('../data_processing/table_beskrivelse.csv')
    return df_cars, df_spesifikasjoner, df_utstyr, df_beskrivelse
'''
name_dtype = df_cars['car_name'].dtype
finnkode_dtype = df_cars['Finnkode'].dtype
link_dtype = df_cars['Link'].dtype
price_dtype = df_cars['Price'].dtype

print(f"datatypes: Name - {name_dtype}, Finnkode - {finnkode_dtype}, Link -  {link_dtype}, Price - {price_dtype}")
'''
def create_specifications_df():
    _, df_spesifikasjoner,_ ,_ = retrieve_data() # Get specs data only
    #access specifications column and convert JSON strings from csv file to Python dictionary
    df_spesifikasjoner['Specifications'] = df_spesifikasjoner['Specifications'].apply(json.loads)
    #Access the labels for each spec
    keys = list(df_spesifikasjoner['Specifications'].iloc[0].keys())
    # Create new columns for each key
    for key in keys:
        df_spesifikasjoner[key] = df_spesifikasjoner['Specifications'].apply(lambda x: x.get(key))

    # Drop the Specifications column, to not contain list of specs
    df_spesifikasjoner = df_spesifikasjoner.drop('Specifications', axis=1)

    return df_spesifikasjoner


if __name__ == "__main__":
     
    df_cars = pd.read_csv('../data_processing/table_car.csv')
    print(f"Cars Datatypes {df_cars.dtypes} \n")
    df_spesifikasjoner = pd.read_csv('../data_processing/table_spesifikasjoner.csv')
    df_utstyr = pd.read_csv('../data_processing/table_utstyr.csv', header=None, names=['Finnkode', 'Equipment'])
    df_beskrivelse = pd.read_csv('../data_processing/table_beskrivelse.csv')

    specifications_df = create_specifications_df()
    #print(f"Specifications: \n {specifications_df.dtypes} \n\n")
    
    print(df_utstyr)

# Explode the Equipment column into separate rows
# Assuming df_utstyr is your DataFrame and it's already loaded

    # Step 1: Explode the 'Equipment' column to separate each item into its own row
    df_utstyr_exploded = df_utstyr.explode('Equipment')

    # Step 2: Count the number of unique equipment items
    unique_equipment_count = df_utstyr_exploded['Equipment'].nunique()

    # Step 3: Count the occurrences of each unique equipment item
    equipment_frequency = df_utstyr_exploded['Equipment'].value_counts()

    # Step 4: Print the results
    print(f"Number of unique equipment items: {unique_equipment_count}")
    print("Frequency of each equipment item:")
    print(equipment_frequency)
    print(f"{specifications_df.head(0)} \n")