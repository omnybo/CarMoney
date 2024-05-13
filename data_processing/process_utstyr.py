from unittest import result
import pandas as pd
import ast
from polyfuzz.models import EditDistance
from polyfuzz import PolyFuzz
from polyfuzz.models import Embeddings
from tqdm import tqdm
from matplotlib import pyplot as plt
def read_data(filepath):
    df_utstyr = pd.read_csv(filepath)
    #Convert list of equipment from dtype str to list(Finnkode, "[""x"",""y""]" => Finnkode,[x,y])
    
    df_utstyr['Equipment'] = df_utstyr['Equipment'].apply(ast.literal_eval)

    
    return df_utstyr
def standarize_equipment(df):
    for idx, row in df.iterrows():
            cleaned_astr = [item.replace('?', '')for item in row['Equipment']if isinstance(item,str)]
            lowercase = [item.lower()  for item in cleaned_astr]
            df.at[idx, 'Equipment'] = lowercase
        
            #Count occurences of equipments
    all_equipment = df['Equipment'].explode().value_counts()
    return df, all_equipment

def low_freq_equipment(equipment_list):
       
    #Find equipments occuring once
    mask_occurs_once = equipment_list == 1
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

def matchesfound(clusters,all_standardized_equipment, min_similarity, ):
    #list of groups
    from_list_flat = [element for sublist in clusters.values() for element in sublist]

    #top equipment list
    top_equipment = all_standardized_equipment.head(50).index.to_list()
    tqdm.write("Initializing PolyFuzz model for matches...")

    model = PolyFuzz("TF-IDF")
    tqdm.write("Matching with top equipment")
    model.match(from_list_flat, top_equipment)
    tqdm.write("Matching with top equipment")
    matches =  model.get_matches()
    best_match = matches[matches['Similarity']>=min_similarity]
    plt.clf()
    visualization = model.visualize_precision_recall(kde=True)
    plt.show()
    
    return matches, best_match,visualization


def apply_standardization(df, best_match):
    # Create a dictionary mapping from original to standardized names
    # Assuming 'From' is the column with original names and 'To' is the column with standardized names
    standardization_map = pd.Series(best_match['To'].values, index=best_match['From']).to_dict()

    # Apply the mapping to each equipment name in the 'Equipment' column
    def standardize_equipment(equipment_list):
        if isinstance(equipment_list, str):
            equipment_list = ast.literal_eval(equipment_list)
            print(equipment_list)
                    # Replace each item in the list with its standardized form, if available
        return [standardization_map.get(item, item) for item in equipment_list]

    df['Equipment'] = df['Equipment'].apply(standardize_equipment)

    return df, standardization_map

def find_matches_with_top_equipment(low_freq_list, top_equipment_list, min_similarity=0.85):
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

def one_hot_encode_equipment(toplist, df_utstyr, csv_name):
    #creating a column of each equipment
    column_names = toplist.index.to_list()
    for equipment in column_names:
        df_utstyr[equipment] = 0


    df_utstyr_dropped = df_utstyr.drop('Equipment', axis=1)
    df_utstyr_dropped.to_csv(csv_name, index=False)
    
if __name__ == "__main__":
    
    #Reading 1st polyfuzz prosessed data
    filepathv0 = 'full_dataset/all_equipments.csv'
    df_utstyr = read_data(filepath=filepathv0)

    #remove special chars and return full equipment list
    df_utstyr_v0,all_equipment = standarize_equipment(df_utstyr)
    exploded = df_utstyr_v0['Equipment'].explode()
    #list of equipment names
    
    equipment_list = all_equipment.index.to_list()

    top_equipment = all_equipment.head(n=37)  
    one_occurence_equipment = low_freq_equipment(all_equipment)
    print(top_equipment)
    
    pd.set_option('display.max_columns',10)
    
    print(f"Number of equipments occuring once: {len(one_occurence_equipment)}")
    print('Total number of equipments:',len(all_equipment.index))
    print(f"Top 37 equipment: \n {top_equipment}")
    
    #polyfuzz model for match clusters:
    result = polyfuzz_grouping(equipment_list)
    print(f"Clusters:\n{result}")
    filename = 'results.txt'
    with open(filename, 'w', encoding='utf-8') as file:
        for key, value in result.items():
            file.write((f"{key:}"))
            if isinstance(value, list):
                for item in value:
                    file.write(f"{item}\n")
            else:
                file.write(f"{value}")
            file.write('\n')
    #find matches with top equipments, and matches above min_similarity
    match, best_match,visualization = matchesfound(result,all_equipment, min_similarity=0.85)
    #plt.savefig('score045.png')
    best_match.to_csv('best_matches.csv')
    match.to_csv('matches.csv')
    pd.options.display.max_rows = 30
    pd.set_option('display.max_columns',10)
    pd.set_option('display.max_columns',100)
    print(f"Matches \n{match}")
    print(f"\n Best Matches:{best_match}")
    print(len(result))
    
    

    # Plotting a histogram of similarity scores
    plt.figure(figsize=(10, 6))
    plt.hist(match['Similarity'], bins=50, color='skyblue')
    plt.title('Histogram of Similarity Scores')
    plt.xlabel('Similarity Score')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()
    
    print(best_match.describe())
    '''
    
    #Reading 1st polyfuzz prosessed data
    filepathv0 = 'data/csv_equipment/equipments_1st_match.csv'
    df_utstyr = read_data(filepath=filepathv0)

    #remove special chars and return full equipment list
    df_utstyr_v0,all_equipment = standarize_equipment(df_utstyr)
    #list of equipment names
    equipment_list = all_equipment.index.to_list()

    top_equipment = all_equipment.head(n=37)  
    one_occurence_equipment = low_freq_equipment(all_equipment)
    print(top_equipment)
    
    print(f"Number of equipments occuring once: {len(one_occurence_equipment)}")
    print('Total number of equipments:',len(all_equipment.index))
    print(f"Top 37 equipment: \n {top_equipment}")
    #polyfuzz model for match clusters:
    '''
    '''
    result = polyfuzz_grouping(equipment_list)

    #find matches with top equipments, and matches above min_similarity
    match, best_match = matchesfound(result,all_equipment, min_similarity=0.73)
    print(best_match)
    new_df, standardization_map = apply_standardization(df=df_utstyr_v0, best_match=best_match)
    new_df.to_csv('data/equipments_2nd_match.csv', index=False)
    print(new_df)
    print('\n Standards: \n')
    print(standardization_map)
    one_hot_encode_equipment(toplist=top_equipment, df_utstyr=new_df)

    #Second polyfuzz processed data?
    filepath_v2 = 'data/equipments_2nd_match.csv'
    df_utstyr2 = read_data(filepath_v2)

    df_utstyr_v2,all_equipment = standarize_equipment(df_utstyr2)
    #list of equipment names
    equipment_list = all_equipment.index.to_list()
    top_equipment = all_equipment.head(n=37)

    one_occurence_equipment = low_freq_equipment(all_equipment)
    print(f"Number of equipments occuring once: {len(one_occurence_equipment)}")
    print('Total number of equipments:',len(all_equipment.index))
    print(f"Top 37 equipment: \n {top_equipment}")

    one_hot_encode_equipment(toplist=top_equipment, df_utstyr=df_utstyr_v2, csv_name='data/equipment_3dd_match_one_hot_encoded.csv')    
    '''
