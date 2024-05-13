import pandas as pd



def print_uncommon(data):
    # Count the occurrences of each 'car_name'
    car_name_counts = data['car_name'].value_counts()

    # Filter 'car_name' values that occur less than five times
    rare_car_names = car_name_counts[car_name_counts < 15]

    # Print the car names with less than five entries
    print("Car names with less than five entries:")
    print(rare_car_names)


def unique_values(data):
    # Find unique values for 'Drivstoff' and 'car_name'
    unique_drivstoff = data['Drivstoff'].unique()
    unique_car_name = data['car_name'].unique()

    # Print the unique values
    print("Unique 'Drivstoff' values:", unique_drivstoff)
    print("Unique 'car_name' values:", unique_car_name)


def encoded_features_main():
    # Load the data to check
    file_path = 'cars_data/cars_withbrand_train.csv'
    file_path2 = 'cars_data/cars_withbrand_test.csv'
    data3 = pd.read_csv(file_path)
    data2 = pd.read_csv(file_path2)
    data = data3.append(data2)


    print_uncommon()
    unique_values(data)



if __name__ == "__main__":
    encoded_features_main()
