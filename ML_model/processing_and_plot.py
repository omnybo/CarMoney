from keras.callbacks import ModelCheckpoint
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from scipy.special import softmax
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings
import shap
from sklearn.model_selection import train_test_split, RandomizedSearchCV

warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', category=DeprecationWarning)


def get_data():
    # get train data
    train_data_path = 'cars_data/clean_train.csv'
    train = pd.read_csv(train_data_path)

    # get test data
    test_data_path = 'cars_data/clean_test.csv'
    test = pd.read_csv(test_data_path)

    return train, test


def get_combined_data():
    # reading train data
    train, test = get_data()

    target = train.SalePrice
    train.drop(['SalePrice'], axis=1, inplace=True)
    test_target = test.SalePrice
    test.drop(['SalePrice'], axis=1, inplace=True)

    combined = train.append(test)
    combined.reset_index(inplace=True)
    combined.drop(['index', 'Id', 'Finnkode'], inplace=True, axis=1)
    # combined.drop(['index', 'Id', 'Finnkode', 'Interioerfarge', 'Hjuldrift', 'modell', 'Maksimaltilhengervekt', 'Girkasse', 'Omregistrering', 'Avgiftsklasse','Antalleiere', 'Rekkevidde', 'Vedlikehold', 'Sylindervolum', 'Antalldoerer', 'Antallseter', 'CO2Utslipp', 'Farge'], inplace=True, axis=1)
    # print(combined)
    return combined, target, test_target





def get_cols_with_no_nans(df, col_type):
    '''
    Arguments :
    df : The dataframe to process
    col_type :
          num : to only get numerical columns with no nans
          no_num : to only get nun-numerical columns with no nans
          all : to get any columns with no nans
    '''
    if (col_type == 'num'):
        predictors = df.select_dtypes(exclude=['object'])
    elif (col_type == 'no_num'):
        predictors = df.select_dtypes(include=['object'])
    elif (col_type == 'all'):
        predictors = df
    else:
        print('Error : choose a type (num, no_num, all)')
        return 0
    cols_with_no_nans = []
    for col in predictors.columns:
        if not df[col].isnull().any():
            cols_with_no_nans.append(col)
    return cols_with_no_nans


def oneHotEncode(df, colNames):
    for col in colNames:
        if (df[col].dtype == np.dtype('object')):
            dummies = pd.get_dummies(df[col], prefix=col)
            #print(dummies)
            # merge the dummies to the dataframe to get the new columns
            df = pd.concat([df, dummies], axis=1)

            # drop the encoded column
            df.drop([col], axis=1, inplace=True)
    return df



def get_and_plot():
    # Load train and test data into pandas DataFrames
    train_data, test_data = get_data()

    # Combine train and test data to process them together
    combined, target, test_target = get_combined_data()

    num_cols = get_cols_with_no_nans(combined, 'num')
    cat_cols = get_cols_with_no_nans(combined, 'no_num')

    print('Number of numerical columns with no nan values :', len(num_cols))
    print('Number of nun-numerical columns with no nan values :', len(cat_cols))
    print(cat_cols)
    combined = combined[num_cols + cat_cols]

    # Plot histogram of our numerical features
    combined.hist(figsize=(12, 10))
    # plt.show()

    # Plot correlation matrix to see the features correlation to SalePrice
    train_data = train_data[num_cols + cat_cols]
    train_data['Target'] = target
    C_mat = train_data.corr()
    fig = plt.figure(figsize=(15, 15))
    sb.heatmap(C_mat, vmax=.8, square=True)
    plt.show()

    # One-hot encode the categorical features
    print('There were {} columns before encoding categorical features'.format(combined.shape[1]))
    combined = oneHotEncode(combined, cat_cols)
    print('There are {} columns after encoding categorical features'.format(combined.shape[1]))

    return combined, target, test_target
