import pandas as pd
import ast
df = pd.read_csv('new_utstyr.csv')

df['Equipment'] = df['Equipment'].apply(ast.literal_eval)
    #Count occurences of equipments
all_equipment = df['Equipment'].explode().value_counts()

print(all_equipment.unique())

def low_freq_equipment(equipment_list):
       
    #Find equipments occuring once
    mask_occurs_once = equipment_list <=1
    items_occurs_once = equipment_list[mask_occurs_once]
    #convert equipment of once/twice occurrence to list and retrieve string(index)
    list_low_freq_equipment = items_occurs_once.index.to_list()

    return list_low_freq_equipment
##before matching: 17493, test1: 10732, test2:
print(low_freq_equipment(all_equipment))

##before matching: 17493, test1: 10732, test2: