from cmath import inf
from os import read, replace
from re import sub
from unittest import result
import pandas as pd
import json
import ast
import numpy as np
import sys
from polyfuzz.models import EditDistance, TFIDF, Embeddings, RapidFuzz
from polyfuzz import PolyFuzz
from collections import defaultdict
from sympy import li
from tqdm import tqdm
def read_data(filepath):
    df_utstyr = pd.read_csv(filepath)
    #Convert list of equipment from dtype str to list(Finnkode, "[""x"",""y""]" => Finnkode,[x,y])
    
    df_utstyr['Equipment'] = df_utstyr['Equipment'].apply(ast.literal_eval)
    #Count occurences of equipments
    all_equipment = df_utstyr['Equipment'].explode().value_counts()
    
    return df_utstyr, all_equipment

def standarize_equipment(df):
    
    for idx, row in df.iterrows():
        cleaned_astr = [item.replace('*','')for item in row['Equipment']if isinstance(item,str)]
        cleaned_quest = [item.replace('?','') for item in cleaned_astr if isinstance(item, str)]
        lowercase = [item.lower()  for item in cleaned_quest]
        df.at[idx, 'Equipment'] = lowercase
        
    return df

def low_freq_equipment(equipment_list):
       
    #Find equipments occuring once
    mask_occurs_once = equipment_list <= 1
    items_occurs_once = equipment_list[mask_occurs_once]
    #convert equipment of once/twice occurrence to list and retrieve string(index)
    list_low_freq_equipment = items_occurs_once.index.to_list()

    return list_low_freq_equipment

def polyfuzz_grouping(list_group):
    tqdm.write("Initializing PolyFuzz model...")
    
    model = PolyFuzz("TF-IDF")
    tqdm.write("Matching...")
    matches = model.match(list_group)
    tqdm.write("Grouping...")
    base_edit_grouper = EditDistance(n_jobs=1)
    model.group(base_edit_grouper)
    tqdm.write("Clustering...")
    matches = model.get_clusters()
    return matches
    #return matches

def matchesfound(clusters,all_standardized_equipment, min_similarity):
    #list of groups
    from_list_flat = [element for sublist in clusters.values() for element in sublist]

    #top equipment list
    top_equipment = all_standardized_equipment.head(50).index.to_list()
    model = PolyFuzz("TF-IDF")

    model.match(from_list_flat, top_equipment)
    matches =  model.get_matches()
    best_match = matches[matches['Similarity']>=min_similarity]
    
    
    return matches, best_match


def apply_standardization(df, best_match, new_filename):
    # Create a dictionary mapping from original to standardized names
    # Assuming 'From' is the column with original names and 'To' is the column with standardized names
    standardization_map = pd.Series(best_match['To'].values, index=best_match['From']).to_dict()

    # Apply the mapping to each equipment name in the 'Equipment' column
    def standardize_equipment(equipment_list):
        if isinstance(equipment_list, str):
            equipment_list = ast.literal_eval(equipment_list)        # Replace each item in the list with its standardized form, if available
        return [standardization_map.get(item, item) for item in equipment_list]

    df['Equipment'] = df['Equipment'].apply(standardize_equipment)
    new_csv = df.to_csv(new_filename, index=False)
    return df, standardization_map, new_csv

def find_matches_with_top_equipment(low_freq_list, top_equipment_list, min_similarity=0.65):
    # Initialize PolyFuzz model for individual string matching
    model = PolyFuzz("TF-IDF")
    all_matches = []

    for top_equip in top_equipment_list:
        # Match the single top equipment against all low-frequency equipment
        model.match([top_equip], low_freq_list)
        matches = model.get_matches()

        # Filter matches by the similarity threshold
        good_matches = matches[matches['Similarity'] >= min_similarity]

        if not good_matches.empty:
            all_matches.extend(good_matches.values.tolist())

    return all_matches

if __name__ == "__main__":
    '''
    filepathv0 = 'full_dataset/all_equipments.csv'
    df_utstyr_v0, all_equipment = read_data(filepath=filepathv0)
    df = standarize_equipment(df_utstyr_v0)
    all_standardized_equipment = df['Equipment'].explode().value_counts()

    equip_list = all_standardized_equipment.index.to_list()    
    top_equipment = all_standardized_equipment.head(50).index.to_list()

    #print(equip_list)
    one_occurence_equipment = low_freq_equipment(all_standardized_equipment)
    print(f"Number of equipments occuring once: {len(one_occurence_equipment)}")
    print('Total number of equipments:',len(all_standardized_equipment.index))
    
    #cluster matches:
    result = polyfuzz_grouping(equip_list)
    print(result)
    #find matches with existing equipment
    m, best_match = matchesfound(result,all_standardized_equipment, min_similarity=0.8)
    print('Match', m,'\n', best_match)
    new_df, standardization_map, new_csv = apply_standardization(df, best_match, new_filename='data/equipment_1st_match.csv')
    #create new csv based on matching
    '''
    
    filepathv1 = 'data/equipment_1st_match.csv'
    df_utstyr_v1, all_equipments = read_data(filepath=filepathv1)
    df_utstyr = standarize_equipment(df_utstyr_v1)
    all_standard_equipment = df_utstyr['Equipment'].explode().value_counts()

    equipment_list = all_standard_equipment.index.to_list()
    once_occur_euqipment = low_freq_equipment(all_standard_equipment)
    print(f"Number of equipments occuring once: {len(once_occur_euqipment)}")
    print('Total number of equipments:',len(all_standard_equipment.index))
    print(f"Top 50 equipment: {all_standard_equipment.head(37)}")
    '''
    result = polyfuzz_grouping(equipment_list)
    print(result)
    #find matches with existing equipment
    m, best_match = matchesfound(result,all_standard_equipment, min_similarity=0.8)
    print('Match', m,'\n', best_match)
    new_df, standardization_map, new_csv = apply_standardization(df_utstyr_v1, best_match, new_filename='data/equipment_2nd_match.csv')
    print(all_standard_equipment.head(37))
    '''
    '''
    filepath_v2 = 'data/equipment_2nd_match.csv'
    df_utstyr_v2, all_equipments_v2 = read_data(filepath=filepath_v2)
    df_utstyrv2 = standarize_equipment(df_utstyr_v2)
    all_standard_equipment_v2 = df_utstyrv2['Equipment'].explode().value_counts()

    equipment_list_v2 = all_standard_equipment_v2.index.to_list()
    once_occur_euqipment_v2 = low_freq_equipment(all_standard_equipment_v2)
    print(f"Number of equipments occuring once: {len(once_occur_euqipment_v2)}")
    print('Total number of equipments:',len(all_standard_equipment_v2.index))
    print(f"Top 50 equipment: {all_standard_equipment_v2.head(37)}")
    #print('Bt matches', matchi)

    result = polyfuzz_grouping(equipment_list_v2)
    print(result)
    #find matches with existing equipment
    matches_v2, best_match_v2 = matchesfound(result,all_standard_equipment_v2, min_similarity=0.75)
    print('Match', matches_v2,'\n', best_match_v2[best_match_v2['Similarity']<=0.75])
    '''
    #creating a csv of top 37 equipment(the same no columns as in specs)
    #creating a column of each equipment
    toplist = all_standard_equipment.head(37).index.to_list()
    for equipment in toplist:
        df_utstyr[equipment] = 0

    for index, row in df_utstyr.iterrows():
        equipments_in_row = row['Equipment']

        for equipment in equipments_in_row:
            if equipment in toplist:
                df_utstyr.at[index, equipment] = 1
    df_utstyr_dropped = df_utstyr.drop('Equipment', axis=1)
    df_utstyr_dropped.to_csv('data/equipment_1st_match_one_hot_encoded.csv', index=False)