from os import replace
import pandas as pd
import json
import ast
import numpy as np
import sys
from polyfuzz.models import EditDistance, TFIDF, Embeddings, RapidFuzz
from polyfuzz import PolyFuzz
from collections import defaultdict
def read_data():
    df_utstyr = pd.read_csv('data/utstyr_new.csv')
    #Convert list of equipment from dtype str to list(Finnkode, "[""x"",""y""]" => Finnkode,[x,y])
    
    df_utstyr['Equipment'] = df_utstyr['Equipment'].apply(ast.literal_eval)
    #Count occurences of equipments
    all_equipment = df_utstyr['Equipment'].explode().value_counts()
    
    return df_utstyr, all_equipment

def standarize_equipment(df):
    
    for idx, row in df_utstyr.iterrows():
        cleaned_equipment = [item.replace(';', '') for item in row['Equipment'] if isinstance(item, str)]
        cleaned_astr = [item.replace('*','')for item in row['Equipment']if isinstance(item,str)]
        lowercase = [item.lower()  for item in cleaned_astr]
        df.at[idx, 'Equipment'] = lowercase
        
    return df

def explode_and_filter_equipment(df):
    # Explode the 'Equipment' lists into individual rows
    exploded_df = df.explode('Equipment')

    unique_equipment = exploded_df['Equipment'].value_counts()
    equipments_to_group = unique_equipment[unique_equipment <= 1].index.to_list()

    return equipments_to_group

def low_freq_equipment(equipment_list):
       
    #Find equipments occuring once
    mask_occurs_once = equipment_list <=1
    items_occurs_once = equipment_list[mask_occurs_once]
    #convert equipment of once/twice occurrence to list and retrieve string(index)
    list_low_freq_equipment = items_occurs_once.index.to_list()

    return list_low_freq_equipment

def polyfuzz_grouping(list_group):
    model = PolyFuzz("TF-IDF")
    matches = model.match(list_group)
    base_edit_grouper = EditDistance(n_jobs=1)
    model.group(base_edit_grouper)
    matches = model.get_clusters()
    return matches
    #return matches

def matchesfound(clusters,all_standardized_equipment):
    #list of groups
    from_list = list(clusters.values())
    from_list_flat = [element for sublist in clusters.values() for element in sublist]

    #top equipment list
    top_equipment = all_standardized_equipment.head(50).index.to_list()
    model = PolyFuzz("TF-IDF")

    model.match(from_list_flat, top_equipment)
    matches =  model.get_matches()
    best_match = matches[matches['Similarity']>=0.75]
    
    
    return matches, best_match
def apply_standardization(df, best_match):
    # Create a dictionary mapping from original to standardized names
    # Assuming 'From' is the column with original names and 'To' is the column with standardized names
    standardization_map = pd.Series(best_match['To'].values, index=best_match['From']).to_dict()

    # Apply the mapping to each equipment name in the 'Equipment' column
    def standardize_equipment(equipment_list):
        # Replace each item in the list with its standardized form, if available
        return [standardization_map.get(item, item) for item in equipment_list]

    df['Equipment'] = df['Equipment'].apply(standardize_equipment)
    return df
def create_batches(lst, n):
    """Yield successive n-sized batches from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
if __name__ == "__main__":
   
    df_utstyr, all_equipment = read_data()

    #removing semi-colons and convert to lowercase
    df = standarize_equipment(df_utstyr)

    all_standardized_equipment = df['Equipment'].explode().value_counts()
    #all_equipment_list = all_standardized_equipment.index.to_list()

    equip_list = all_standardized_equipment.index.to_list()

    #cluster matches:
    result = polyfuzz_grouping(equip_list)

    #find matches with existing equipment
    m, best_match = matchesfound(result,all_standardized_equipment)
    print('Match', m,'\n', best_match)

    new_df = apply_standardization(df, best_match)
    new_csv = new_df.to_csv('new_utstyr.csv',index=False)
    
    clean_data = pd.read_csv('new_utstyr.csv')
    print(clean_data.columns)
    