import xgboost as xgb
import catboost as cb
import sklearn as sk
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
import scikitplot as skplt
import pandas as pd
import numpy as np

class FactorModel():
    def __init__(self, data):
        self.data = data
        self.model = None
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None
        self.scaler_x = None
        self.scaler_y=None
        self.factors= None
        self.stdz_data=None
        self.stdz_ret= None

    def prep_data(self, target, factors, n=.4, random_state=17, layers=None):
        self.factors = factors
        # Drop rows where target column contains NA
        self.data = self.data.dropna(subset=[target])
        
        # Standardize the features to have mean=0 and variance=1
        self.scaler_x = sk.preprocessing.StandardScaler()
        self.scaler_y = sk.preprocessing.StandardScaler()
        self.data.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Fill NAs and normalize data according to specified layers
        if layers:
            for layer in layers:
                # Group data by each layer
                group = self.data.groupby(layer)
                for factor in factors:
                    # For each factor, fill NAs with group mean and apply standard scaling
                    self.data[factor] = group[factor].transform(lambda x: x.fillna(x.mean()))
                    self.data[factor] = group[factor].transform(lambda x: (x - x.mean()) / x.std())
                    # replace infinity values by NaN
                    self.data[factor].replace([np.inf, -np.inf], np.nan, inplace=True)
                    # fill NaN values with mean of each group
                    self.data[factor].fillna(self.data.groupby(layer)[factor].transform('mean'), inplace=True)
        else:
            # Fill NAs with column mean
            self.data.fillna(self.data.mean(), inplace=True)

        self.data= self.data.dropna()
        

        # Standardize the data and target
        self.stdz_data = self.scaler_x.fit_transform(self.data[factors])  
        self.stdz_ret = pd.qcut(self.data[target], q=5, labels=False)
        # Define target and features
        X = self.stdz_data.copy()
        y = self.stdz_ret.copy()

        # Create a train/test split. n can be a fraction between 0 and 1 to indicate the percentage split
        self.X_train, self.X_test, self.y_train, self.y_test = sk.model_selection.train_test_split(
            X, y, test_size=n, random_state=random_state)
        
    def train(self, model_types=['xgboost']):
        self.models = {}
        for model_type in model_types:
            if model_type == 'xgboost':
                model = xgb.XGBClassifier()
            elif model_type == 'catboost':
                model = cb.CatBoostClassifier(verbose=0)
            elif model_type == 'sk_dtree':
                model = DecisionTreeClassifier()
            elif model_type == 'sk_rf':
                model = RandomForestClassifier(max_depth=25)
            model.fit(self.X_train, self.y_train)
            self.models[model_type] = model

    def evaluate(self):
        for model_type, model in self.models.items():
            print(f"Evaluating model: {model_type}")
            preds = model.predict(self.X_test)
            self.draw_confusion_matrix(preds)
            self.draw_roc_curve(preds)
            self.plot_feature_importance(model, model_type)
            
    # Updating plot_feature_importance to accept model and model_type as inputs
    def plot_feature_importance(self, model, model_type):
        try:
            importances = model.feature_importances_
            feature_importances = dict(zip(self.factors, importances))
            sorted_feature_importances = sorted(feature_importances.items(), key=lambda x: x[1])
            features = [x[0] for x in sorted_feature_importances]
            importance_values = [x[1] for x in sorted_feature_importances]
            plt.figure(figsize=(10,8))
            plt.barh(features, importance_values, color='lightgreen')
            plt.title(f'Features Importance for {model_type}')
            plt.show()
        except Exception as e:
            print(f"An error occurred: {e}")


    def predict(self, X):
        return self.model.predict(X)
        
    def draw_confusion_matrix(self, preds):
        cm = sk.metrics.confusion_matrix(self.y_test, preds)
        skplt.metrics.plot_confusion_matrix(self.y_test, preds, normalize=True)

    def draw_roc_curve(self, preds):
        # Binarize the output
        y_test = sk.preprocessing.label_binarize(self.y_test, classes=[0, 1, 2, 3, 4])
        preds = sk.preprocessing.label_binarize(preds, classes=[0, 1, 2, 3, 4])

        # Compute ROC curve and ROC area for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for i in range(5):    # assuming you have 5 classes
            fpr[i], tpr[i], _ = sk.metrics.roc_curve(y_test[:, i], preds[:, i])
            roc_auc[i] = sk.metrics.auc(fpr[i], tpr[i])

        # Plotting ROC curves for the multiclass problem
        plt.figure()
        for i in range(5):    # assuming you have 5 classes
            plt.plot(fpr[i], tpr[i],
                    label='ROC curve of class {0} (area = {1:0.2f})'
                    ''.format(i, roc_auc[i]))

        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Multi-class ROC curve')
        plt.legend(loc="lower right")
        plt.show()
    def predict_full_data(self):
        predictions = self.scaler_x.transform(self.data[self.factors])
        for model_name, model in self.models.items():
            preds = model.predict(predictions)
            
            if len(preds.shape) == 1:   # The predictions is a 1D array
                # Make the preds a column vector
                preds = preds[:, np.newaxis]
            
            # Convert the predictions into a DataFrame
            preds_df = pd.DataFrame(preds, 
                                    index=self.data.index, 
                                    columns=[f'{model_name}_pred' for i in range(preds.shape[1])])

            # Bucket predictions into quintiles for each class and add to the original dataset
            for col in preds_df.columns:
                self.data[col] = pd.qcut(preds_df[col].rank(method='first'), q=5, labels=False)