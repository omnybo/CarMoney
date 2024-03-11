import pandas as pd
import json
import ast
import numpy as np
import sys
from sklearn.preprocessing import MultiLabelBinarizer
from rapidfuzz import process,fuzz
from polyfuzz import PolyFuzz
from polyfuzz.models import TFIDF
def read_data():
    df_utstyr = pd.read_csv('../data/utstyr_new.csv')
    #Convert list of equipment from dtype str to list(Finnkode, "[""x"",""y""]" => Finnkode,[x,y])
    
    df_utstyr['Equipment'] = df_utstyr['Equipment'].apply(ast.literal_eval)
    #Count occurences of equipments
    all_equipment = df_utstyr['Equipment'].explode().value_counts()
    
    return df_utstyr, all_equipment

def standarize_equipment(df):

    abs_bremser_versions = ['ABS-bremser', 'abs-bremser','ABS-bremse' 'blokkeringsfritt bremsesystem (abs)','abs bremser', 'abs- bremser',
                        'abs','anti-lock bremser (abs)','abs (antiblokkeringsbremsesystem)','0067 ABS']
    ryggesensor_versions = ['RSA01 - Ryggesensor', '-Ryggesensor',' *Ryggesensor', 'Ryggesensorer',
                            'ryggesensor','508   PARKING SENSORS']
    
    ryggekamera_versions = ['Ryggekame','Rygge tv','Ryggekmaera','- Ryggekamera med visning i fargeskjerm',
                            'Ryggekamera med visning i fargeskjerm','KA2 Med ryggekamerasystem (type 2)', 'Med ryggekamerasystem (type 1)']
    #convert all abs equipment to lowercase:
    regnsensor_versions = ['345 Regensensor', 'Regnesensor', '345 Regnsensor','Regnsensor','RS01 Regnsensor','RS01 Regnsensor', 'RS01 - Regnsensor'] 
    
    el_vinduer_versions = ['El. vinduer', 'El vinduer', 'El vinduer foran og bak','Elektrisk vinduer', 'Elektriske hvinduer','- El vinduer', 'EL vinduer'] 
 
    lowercase_abs = [version.lower() for version in abs_bremser_versions]
    abs_standard = 'ABS-Bremser'
    
    lowercase_ryggesensor =[version.lower() for version in ryggesensor_versions]
    ryggesensor_standard =  'Ryggesensor' 
    
    lowercase_ryggekamera =[version.lower() for version in ryggekamera_versions]
    ryggekamera_standard =  'Ryggekamera' 
    
    lowercase_regnsensor =[version.lower() for version in regnsensor_versions]
    regnsensor_standard =  'Regnsensor' 
    
    lowercase_el_vinduer =[version.lower() for version in el_vinduer_versions]
    el_vinduer_standard =  'El.vinduer' 
    
    parkvarme_substring = 'parkeringsvarme'
    parkvarme_standard = 'Parkeringsvarmer'
    
    airbag_substring = 'airbag'
  
    for idx, row in df_utstyr.iterrows():
        new_equipment_list = [abs_standard if equipment.lower() in lowercase_abs 
                              else ryggesensor_standard if equipment.lower() in lowercase_ryggesensor 
                              else ryggekamera_standard if equipment.lower() in lowercase_ryggekamera
                              else parkvarme_standard if parkvarme_substring in equipment.lower()
                              else regnsensor_standard if equipment.lower() in lowercase_regnsensor
                              else el_vinduer_standard if equipment.lower() in lowercase_el_vinduer
                              
                              else equipment for equipment in row['Equipment']]
        
        #Update the row's equipment list with the new list that has standardized ABS names
        df.at[idx, 'Equipment'] = new_equipment_list
         
    return df

def explode_and_filter_equipment(df):
    # Explode the 'Equipment' lists into individual rows
    exploded_df = df.explode('Equipment')

    unique_equipment = exploded_df['Equipment'].value_counts()
    equipments_to_group = unique_equipment[unique_equipment <= 1].index.to_list()

    return equipments_to_group

def fuzzy_grouping_test():
    abs_bremser_versions = ['ABS-bremser', 'abs-bremser','ABS-bremse' 'blokkeringsfritt bremsesystem (abs)','abs bremser', 'abs- bremser',
                        'abs','anti-lock bremser (abs)','abs (antiblokkeringsbremsesystem)','0067 ABS']
    abs_standard = ['abs Bremser', 'abs-Bremser']
    regnsensor_versions = ['345 Regensensor', 'Regnesensor', '345 Regnsensor','Regnsensor','RS01 Regnsensor','RS01 Regnsensor', 'RS01 - Regnsensor'] 
    
    model = PolyFuzz("TF-IDF")
    model.match(abs_bremser_versions)
    
    #get matches of model dataframe
    matches = model.get_matches()
    print(matches)
    #filter values >=1
    similarities = matches['Similarity']>=1
    result = matches[similarities]
    print(result)
    
    print('----Regnsensor---- \n')
    model = PolyFuzz("TF-IDF")
    model.match(regnsensor_versions)
    
    #get matches of model dataframe
    matches_sensor = model.get_matches()
    print(matches_sensor)
    
    #filter values >=1
    similarities = matches_sensor['Similarity']>=1
    result_sensor = matches_sensor[similarities]
    print('\n',result_sensor)
    
    list2 = matches_sensor['Similarity'].to_list()
    print(list2)
    
    threshold = 0.75
    #Print similarities above 0.85
    for i in list2:
        if i >= threshold:
            print(i)
        else:
            print('Below threshold')

def fuzzy_matching_top_equipment(all_equipment,top_equipment):

    matching_model = PolyFuzz("TF-IDF")
    equipment_to_match = matching_model.match(all_equipment, top_equipment)
    matching_model.group(link_min_similarity=0.75 )
    matches = equipment_to_match.get_matches()
    
    min_similarity = matches[matches['Similarity'] <= 0.5]
    

    '''
    #result = matches[min_similarity] 
    #print(type(min_similarity), min_similarity.head(2))
    #matches['Group'] = list(zip(matches['Similarity'],matches['From']))
    #no_grouping = result_similarity.index.to_list()
    #print('Equipment with low similarity (less than 0.2):')
    #for index, row in min_similarity.iterrows():
        #print(f"{row['From']} -> {row['To']}: {row['Similarity']}")
    #similarities = matches[matches['Similarity'] >= link_min_similarity]
    '''
    matches.to_csv('equipment_matches.csv', index=False)
    return min_similarity
def group_matches():
    df = pd.read_csv('../data_processing/equipment_matches.csv')
    groups = []
    for index, row in df.iterrows():
        if row['similarity'] >= 0.65:
            df.at[index,'From'] = 'St'
if __name__ == "__main__":

    df_utstyr, all_equipment = read_data()
    #print('Columns df:\n', df_utstyr.columns,'\n')
    #print(f"All equipment before standarization: \n {all_equipment}\n")
    new_df = standarize_equipment(df_utstyr)
    
    all_standardized_equipment = new_df['Equipment'].explode().value_counts()
    #print('No of equipment after stadnarization \n', all_standardized_equipment)
    
    all_equipment_list = all_standardized_equipment.index.to_list()
    
    
    top_20_equipment = all_standardized_equipment.head(20).index.to_list()
    #retrieve equipment occuring once or twice
    
    #Find equipments occuring once
    mask_occurs_once = all_standardized_equipment <=1
    items_occurs_once = all_standardized_equipment[mask_occurs_once]
    #convert equipment of once/twice occurrence to list and retrieve string(index)
    items_output_list = items_occurs_once.index.to_list()
    
    equipment_matches = fuzzy_matching_top_equipment(items_output_list,top_20_equipment)
    
    
    
    
    '''
    with open('output.txt', 'w', encoding='utf-8') as f:
        # Write the string representation of the Series to the file
        f.write(items_output_str)
        # Print the equipment items that occur only once
    '''
    '''
    equipments_to_group = explode_and_filter_equipment(new_df)
    fuzzy_grouping_equipment = fuzzy_grouping(equipments_to_group)

    # Example output of the grouping result
    
    with open('output.txt', 'w', encoding='utf-8') as f:
        for standard, variants in fuzzy_grouping_equipment.items():
            if len(variants) > 1:
                f.write(f"Standard: {standard}, Variants: {variants}")
    '''
    
    '''
    model = PolyFuzz("TF-IDF")
    model.match(items_output_list)
    matches = model.get_matches()
    #for same word but different case: partial_token_ratio or partial_token_set_ratio
    with open('polyfuzz_grouping.txt', 'w', encoding='utf-8') as f:
        for index, row in matches.iterrows():
            f.write(f"From: {row['From']}, To: {row['To']}, Similarity: {row['Similarity']}\n")
    '''