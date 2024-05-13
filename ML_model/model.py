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
from processing_and_plot import get_and_plot

warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', category=DeprecationWarning)


def split_combined(combined):
    train = combined[:33522]
    test = combined[33522:]

    return train, test


def make_submission(prediction, sub_name):
    my_submission = pd.DataFrame({'Id': pd.read_csv('cars_data/clean_test.csv').Id, 'SalePrice': prediction})
    my_submission.to_csv('{}.csv'.format(sub_name), index=False)
    print('A submission file has been made')


def shap_analysis(model, test):
    samples = shap.sample(test, 100)
    explainer = shap.KernelExplainer(model.predict, samples)
    shap_values = explainer.shap_values(test,nsamples=100)
    shap.summary_plot(shap_values,test,title='RFModel')


def RandomForest_model(train, test, target, test_target):
    # Random forest model
    RFModel = RandomForestRegressor()
    RFModel.fit(train, target)

    predicted_train_RF = RFModel.predict(train)
    predicted_test_RF = RFModel.predict(test)

    MAEtrain = mean_absolute_error(target, predicted_train_RF)
    MAEtest = mean_absolute_error(test_target, predicted_test_RF)
    print('Random forest validation train MAE = ', MAEtrain)
    print('Random forest validation test MAE = ', MAEtest)


    # samples = shap.sample(train, 100)
    predicted_prices = RFModel.predict(test)
    make_submission(predicted_prices, 'predictions/cars_RF')
    make_submission(test_target, 'predictions/correct_prices')

    #samples = shap.sample(test, 100)
    # explainer = shap.KernelExplainer(RFModel.predict, samples)
    # shap_values = explainer.shap_values(test,nsamples=100)
    # shap.summary_plot(shap_values,test,title='RFModel')
    return RFModel


def DNN_model(train, test, target, test_target):
    NN_model = Sequential()
    NN_model.add(Dense(128, kernel_initializer='normal', input_dim=train.shape[1], activation='relu'))
    NN_model.add(Dense(256, kernel_initializer='normal', activation='relu'))
    NN_model.add(Dense(256, kernel_initializer='normal', activation='relu'))
    NN_model.add(Dense(512, kernel_initializer='normal', activation='relu'))
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
    history = NN_model.fit(train, target, epochs=100, batch_size=16, validation_split=0.2,
                           callbacks=callbacks_list)

    # Plot the MAE during training
    plt.plot(history.history['mean_absolute_error'], label='Training MAE')
    plt.plot(history.history['val_mean_absolute_error'], label='Validation MAE')
    plt.xlabel('Epoch')
    plt.ylabel('MAE')
    plt.title('MAE during Training')
    plt.legend()
    plt.show()

    # Find the best checkpoint
    best_epoch = history.history['val_loss'].index(min(history.history['val_loss']))
    best_checkpoint = f'Weights-{best_epoch + 1:03d}--{min(history.history["val_loss"]):.5f}.hdf5'

    # Load weights from the best checkpoint
    NN_model.load_weights(best_checkpoint)
    NN_model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_absolute_error'])

    # Predict using the trained model
    predictions = NN_model.predict(test)
    MAE = mean_absolute_error(test_target, predictions)
    print('Neural network model test MAE = ', MAE)
    make_submission(predictions[:, 0], 'predictions/cars_NN')

    return NN_model


def RF_hyperparameters(train, test, target, test_target):
    # Define the model
    rf = RandomForestRegressor(random_state=42)

    # Specify parameters we want to check
    param_dist = {
        'criterion': ['friedman_mse'],
        'n_estimators': [305, 310, 315],
        'max_features': ['sqrt'],
        'max_depth': [32],
        'min_samples_split': [2],
        'min_samples_leaf': [1],
        'bootstrap': [False]
    }

    # Setup RandomizedSearchCV
    random_search = RandomizedSearchCV(estimator=rf,
                                       param_distributions=param_dist,
                                       n_iter=100,
                                       cv=3,
                                       verbose=2,
                                       random_state=42,
                                       n_jobs=-1)

    # Fit RandomizedSearchCV
    random_search.fit(train, target)

    # Best model
    best_rf = random_search.best_estimator_

    # Predict the prices
    predictions = best_rf.predict(test)

    # Evaluation using MAE
    mae = mean_absolute_error(test_target, predictions)
    print(f"Best parameters: {random_search.best_params_}")
    print(f"Test MAE: {mae}")


def NN_hyperparmeters(train, test, target, test_target):
    def build_model(hp):
        model = Sequential()
        model.add(Dense(hp.Int('input_units', min_value=32, max_value=512, step=32),
                        input_dim=train.shape[1], activation='relu'))

        for i in range(hp.Int('n_layers', 1, 6)):  # Number of hidden layers
            model.add(Dense(hp.Int(f'dense_{i}_units', min_value=32, max_value=256, step=32),
                            activation=hp.Choice('dense_activation', values=['relu', 'tanh', 'sigmoid'])))

        model.add(Dense(1, activation='linear'))  # Output layer
        model.compile(optimizer=keras.optimizers.Adam(
            hp.Float('learning_rate', min_value=1e-4, max_value=1e-2, sampling='LOG')),
            loss='mean_absolute_error', metrics=['mean_absolute_error'])
        return model

    # Instantiate the tuner
    tuner = RandomSearch(
        build_model,
        objective='val_mean_absolute_error',
        max_trials=10,  # Number of variations on model
        executions_per_trial=10,  # Number of times to train each model variation
        directory='my_dir',
        project_name='keras_tuning'
    )

    # Perform hypertuning
    tuner.search(train, target, epochs=50, validation_data=(test, test_target))

    # Get the optimal hyperparameters
    best_hps = tuner.get_best_hyperparameters(num_trials=10)[0]

    print(best_hps)
    # Build the model with the optimal hyperparameters
    model = tuner.hypermodel.build(best_hps)
    history = model.fit(train, target, epochs=50, validation_data=(test, test_target))

    # Evaluate the performance of the model with the best hyperparameters
    eval_result = model.evaluate(test, test_target)
    print("[test loss, test accuracy]:", eval_result)
    

def main():
    # Get and process the data
    combined, target, test_target = get_and_plot()
    train, test = split_combined(combined)

    # Random Forest
    #RFmodel = RandomForest_model(train, test, target, test_target)
    #shap_analysis(RFmodel, test)

    #Deep Neural Network
    NNmodel = DNN_model(train, test, target, test_target)
    #shap_analysis(NNmodel, test)


if __name__ == "__main__":
    main()


