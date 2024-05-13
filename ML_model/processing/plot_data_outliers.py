import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_outliers(data, numerical_cols):
    plt.figure(figsize=(12, 6))
    for index, col in enumerate(numerical_cols, start=1):
        plt.subplot(1, len(numerical_cols), index)
        sns.boxplot(y=data[col])
        plt.title(f'Box Plot of {col}')

    plt.tight_layout()
    plt.show()

def plot_data_histogram(data, numerical_cols):
    plt.figure(figsize=(12, 6))
    for index, col in enumerate(numerical_cols, start=1):
        plt.subplot(1, len(numerical_cols), index)
        sns.histplot(data[col], kde=True, bins=30)
        plt.title(f'Histogram of {col}')
        plt.axvline(data[col].mean(), color='k', linestyle='dashed', linewidth=1)
        plt.axvline(data[col].median(), color='red', linestyle='dashed', linewidth=1)

    plt.tight_layout()
    plt.show()


def plot_outliers_main():
    # Load the data to check
    file_path = 'cars_data/cars_withbrand_train.csv'
    data = pd.read_csv(file_path)

    data['Alder'] = 2024 - data['Modellaar']  # Changing the feature to age and not year
    # Numerical columns we want to see outliers from
    numerical_cols = ['Kilometer', 'Effekt', 'Vekt', 'Alder', 'SalePrice']

    # The plots
    plot_outliers(data, numerical_cols)
    plot_data_histogram(data, numerical_cols)


if __name__ == "__main__":
    plot_outliers_main()