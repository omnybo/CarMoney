from keras.callbacks import ModelCheckpoint
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from matplotlib import pyplot as plt
from scipy.special import softmax
import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import xgboost
import warnings
warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', category=DeprecationWarning)
import shap


def get_data():
    # get train data
    train_data_path = 'cars_6000_train.csv'
    train = pd.read_csv(train_data_path)

    # get test data
    test_data_path = 'cars_6000_test.csv'
    test = pd.read_csv(test_data_path)

    return train, test

def get_combined_data():
    # reading train data
    train, test = get_data()

    target = train.SalePrice
    train.drop(['SalePrice'], axis=1, inplace=True)

    combined = train.append(test)
    combined.reset_index(inplace=True)
    combined.drop(['index', 'Id', 'Finnkode'], inplace=True, axis=1)
    print(combined)

    return combined, target

# Load train and test data into pandas DataFrames
train_data, test_data = get_data()

# Combine train and test data to process them together
combined, target = get_combined_data()



def get_cols_with_no_nans(df,col_type):
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
    else :
        print('Error : choose a type (num, no_num, all)')
        return 0
    cols_with_no_nans = []
    for col in predictors.columns:
        if not df[col].isnull().any():
            cols_with_no_nans.append(col)
    return cols_with_no_nans

num_cols = get_cols_with_no_nans(combined , 'num')
cat_cols = get_cols_with_no_nans(combined , 'no_num')

print ('Number of numerical columns with no nan values :',len(num_cols))
print ('Number of nun-numerical columns with no nan values :',len(cat_cols))

combined = combined[num_cols + cat_cols]
combined.hist(figsize = (12,10))
plt.show()

train_data = train_data[num_cols + cat_cols]
train_data['Target'] = target

C_mat = train_data.corr()
fig = plt.figure(figsize = (15,15))

sb.heatmap(C_mat, vmax = .8, square = True)
plt.show()


def oneHotEncode(df,colNames):
    for col in colNames:
        if( df[col].dtype == np.dtype('object')):
            dummies = pd.get_dummies(df[col],prefix=col)
            df = pd.concat([df,dummies],axis=1)

            #drop the encoded column
            df.drop([col],axis = 1 , inplace=True)
    return df


print('There were {} columns before encoding categorical features'.format(combined.shape[1]))
combined = oneHotEncode(combined, cat_cols)
print('There are {} columns after encoding categorical features'.format(combined.shape[1]))


def split_combined():
    global combined
    train = combined[:5850] # Need to change after final data
    test = combined[5850:]

    return train, test


train, test = split_combined()



# Make DNN

NN_model = Sequential()
NN_model.add(Dense(128, kernel_initializer='normal', input_dim=train.shape[1], activation='relu'))
NN_model.add(Dense(256, kernel_initializer='normal', activation='relu'))
NN_model.add(Dense(256, kernel_initializer='normal', activation='relu'))
NN_model.add(Dense(256, kernel_initializer='normal', activation='relu'))
NN_model.add(Dense(1, kernel_initializer='normal', activation='linear'))

NN_model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_absolute_error'])
NN_model.summary()

# Define the checkpoint
checkpoint_name = 'Weights-{epoch:03d}--{val_loss:.5f}.hdf5'
checkpoint = ModelCheckpoint(checkpoint_name, monitor='val_loss', verbose=1, save_best_only=True, mode='auto')
callbacks_list = [checkpoint]

# Train DNN
history = NN_model.fit(train, target, epochs=100, batch_size=16, validation_split=0.20, callbacks=callbacks_list)

# Find the best checkpoint
best_epoch = history.history['val_loss'].index(min(history.history['val_loss']))
best_checkpoint = f'Weights-{best_epoch+1:03d}--{min(history.history["val_loss"]):.5f}.hdf5'

# Load weights from the best checkpoint
NN_model.load_weights(best_checkpoint)
NN_model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_absolute_error'])

# Predict using the trained model
predictions = NN_model.predict(test)
#print(predictions)


def make_submission(prediction, sub_name):
  my_submission = pd.DataFrame({'Id':pd.read_csv('cars_6000_test.csv').Id,'SalePrice':prediction})
  my_submission.to_csv('{}.csv'.format(sub_name),index=False)
  print('A submission file has been made')

make_submission(predictions[:,0],'cars_NN')



# Use shap on NN model
samples = shap.sample(train, 100)
explainer = shap.KernelExplainer(NN_model.predict, samples)
shap_values = explainer.shap_values(test,nsamples=100)
shap.summary_plot(shap_values[0],test, title='NNModel')


#shap.summary_plot(shap_values,test)

#shap.initjs()
#shap.force_plot(explainer.expected_value, shap_values[0,:]  ,test[0,:])






# XGBoost model
XGBModel = xgboost.XGBRegressor().fit(train, target)

predicted_pricesXG = XGBModel.predict(train)
MAE = mean_absolute_error(target, predicted_pricesXG)
print('XGBoost validation MAE = ', MAE)

XGB_predictions = XGBModel.predict(test)
make_submission(XGB_predictions,'cars_XGB')


# Use shap on XGBoost
explainer = shap.KernelExplainer(XGBModel.predict, samples)
shap_values = explainer.shap_values(test,nsamples=100)

shap.summary_plot(shap_values,test,title='XGBModel')
#shap.plots.beeswarm(shap_values)
#shap.plots.bar(shap_values)
#shap.summary_plot(shap_values, plot_type='violin')
#shap.plots.bar(shap_values[0])
#shap.plots.waterfall(shap_values[0])
#shap.plots.force(shap_values[0])


#explainerX = shap.Explainer(XGBModel)
#shap_valuesX = explainerX(test)
#shap.plots.waterfall(shap_valuesX[0])
#shap.summary_plot(shap_valuesX,test)
#shap.summary_plot(shap_valuesX[0],test)




# Random forest model
RFModel = RandomForestRegressor()
RFModel.fit(train, target)

predicted_pricesRF = RFModel.predict(train)
MAE = mean_absolute_error(target, predicted_pricesRF)
print('Random forest validation MAE = ', MAE)

predicted_prices = RFModel.predict(test)
make_submission(predicted_prices,'cars_RF')

explainer = shap.KernelExplainer(RFModel.predict, samples)
shap_values = explainer.shap_values(test,nsamples=100)

shap.summary_plot(shap_values,test,title='RFModel')




