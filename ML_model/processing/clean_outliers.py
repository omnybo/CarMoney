import pandas as pd
from sklearn.model_selection import train_test_split


def cap_outliers(data):
    # The numerical columns we want to check for outliers
    data['Alder'] = 2024 - data['Modellaar']  # Changing the feature to age and not year
    data.drop(['Modellaar'], inplace=True, axis=1)
    # Define numerical columns for which you want to handle outliers for
    numerical_cols = ['Kilometer', 'Effekt', 'Vekt', 'Alder', 'SalePrice']

    # Handling outliers
    for col in numerical_cols:
        # Calculate Q1 (25th percentile of the data) for the given column
        Q1 = data[col].quantile(0.25)
        # Calculate Q3 (75th percentile of the data) for the given column
        Q3 = data[col].quantile(0.75)
        # Define the Interquartile Range (IQR)
        IQR = Q3 - Q1

        # Define bounds for outliers
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Cap outliers
        data[col] = data[col].clip(lower=lower_bound, upper=upper_bound)


def save_new_data(data):
    train, test = train_test_split(data, test_size=0.2, random_state=42)

    # Save the cleaned data to a new CSV file
    train_path = 'cars_data/clean_train.csv'
    test_path = 'cars_data/clean_test.csv'
    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)
    print(f"Cleaned data saved")


def clean_outliers_main():
    # Load the data to check
    file_path = 'cars_data/cars_withbrand_train.csv'
    file_path2 = 'cars_data/cars_withbrand_test.csv'
    data3 = pd.read_csv(file_path)
    data2 = pd.read_csv(file_path2)
    data = data3.append(data2)

    capped_data = cap_outliers(data)

    save_new_data(capped_data)


if __name__ == "__main__":
    clean_outliers_main()