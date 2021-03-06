# -*- coding: utf-8 -*-
"""Breast_Cancer_Diag.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17xYwFP499tzCxC2BnTwVt-H9V8fZxbj7
"""

# Commented out IPython magic to ensure Python compatibility.
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)
# %matplotlib inline
from google.colab import files
import pandas as pd
pd.options.display.float_format = '{:.2f}'.format # uppress scientific notation
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
# %reload_ext sql
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from plotly.offline import iplot
import plotly.express as px
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline

# Declare your Github Repository address
git_url='https://raw.githubusercontent.com/phuongvnguyen/The-Breast-Cancer-Diagnostic/master/datasets_180_408_data.csv'

class Data_Extraction():
  """
  This class is to extract data from the csv file stored in the Github repos
  """

  def __init__(self,git_url):
    print('\033[1m'+'Please, wait! I am extracting data from your Github Repository'+'\033[0m'+'\n...')
    self.git_url=git_url
    self.data=self.load_data(self.git_url)
    
  def load_data(self,url):
    self.data=pd.read_csv(url)
    print('Data was successfully extracted!')
    return self.data

class Data_Information():
  """
  This class is to obtain the basic understanding of data, such as: first five observation,
  the number of columns, observations, etc.
  """

  def __init__(self,Extract):
    self.data=Extract.data 
    self.general_infor(self.data,5)

  def general_infor(self,data,number_obs):
    print('The first %d: observations \n'%number_obs)
    display(self.data.head(number_obs))
    print('The general information:\n')
    display(data.info())

class Data_Engineering():
  """
  This class is to transform data. In particular, there is a unnamed column in the dataset. Thus,
  we drop it. On the other hand, we replace the diagnosis of malignant or benign with 1s and 0s.
  Meanwhile, we standardize data. Finally, we split data into the train and test samples
  """

  def __init__(self,Extract):
    print('\033[1m'+'I am engineering data'+'\033[0m'+'\n...')
    self.data=Extract.data
    self.cleaned_data=self.cleaner(self.data)
    self.X, self.y=self.standardizer(self.cleaned_data)
    self.X_train, self.X_test, self.y_train, self.y_test=self.splitter(self.X, self.y)
    

  def cleaner(self,data):
    self.data=data.drop(columns=['Unnamed: 32', 'id'])
    self.data['diagnosis'].replace({'M':1, 'B':0}, inplace = True)
    return self.data

  def standardizer(self,data):
    self.X=data.iloc[:, 1:].values
    self.X= StandardScaler().fit_transform(self.X)
    self.y=data['diagnosis']
    return self.X, self.y

  def splitter(self,X,y):
    self.X_train, self.X_test, self.y_train, self.y_test=train_test_split(X, y, test_size = 0.25, random_state = 0)
    print('X train:', self.X_train.shape)
    print('X test:', self.X_test.shape)
    print('y train:', self.y_train.shape)
    print('y test:', self.y_test.shape)
    print('I am done!')
    return self.X_train, self.X_test, self.y_train, self.y_test

class Model_Selector():
  """
  This class is to conduct the spot-check classification algorithms, such as
  1. Logistic Regression.
  2. Support Vector Machines.
  3. k-Nearest Neighbors.
  4. Linear Discriminant Analysis.
  The 10-fold cross validation procedure is used to evaluate each algorithm.
  Also, Area under ROC Curve (or AUC for short), which is a performance metric for binary classication 
  problems is used.
  """

  def __init__(self,Data_Engineering):
    self.X=Data_Engineering.X
    self.y=Data_Engineering.y
    self.models=self.models()
    self.results, self.names=self.models_comparer(self.models,self.X,self.y)
    self.plot_results(self.results, self.names)

  def models(self):
    self.models=[]
    self.models.append(('Logistic',LogisticRegression()))
    self.models.append(('Linear-Discriminant-Analysis',LinearDiscriminantAnalysis()))
    self.models.append(('Support-Vector-Class',SVC()))
    self.models.append(('K-Nearest-Class',KNeighborsClassifier()))
    return self.models 

  def models_comparer(self,models, X,y):
    print('\033[1m'+'I am comparing the performance of %d algorithms by using 10-Fold Cross Validation and ROC-AUC'%len(models)+'\033[0m'+'\n...')
    self.results=[]
    self.names=[]
    for self.name,self.model in models:
      self.kfold=KFold(n_splits=5,random_state=7)
      self.cv_results=cross_val_score(self.model,X,y,cv=self.kfold,scoring='roc_auc')
      self.results.append(self.cv_results)
      self.names.append(self.name)
      self.msg='%s: %f (%f)'%(self.name, self.cv_results.mean(),self.cv_results.std())
      print(self.msg)
    return self.results, self.names

  def plot_results(self,results,names):
    self.fig=plt.figure(figsize=(10,6))
    self.fig.suptitle('Model Performance Comparision (AUROC)')
    self.ax=self.fig.add_subplot(111)
    plt.boxplot(results)
    self.ax.set_xticklabels(names)
    self.ax.grid(True)
    plt.show()
    print('I am done!')

class Model_Validator():
  """
  This class includes a number of tools, which are used to validate the performance of a particular model.
  - Confusion matrix.
  - Figure of Area Under Receiver Operating Characteristics (AUROC) Curve.
  Beside, this class is used to do the forecasting and tune the model hyperparameters.
  """

  def Predictor(self,model,X):
    print('I am doing the out-of-sample forecasts\n...')
    self.y_pred=model.predict(X)
    self.prob_pred=model.predict_proba(X)
    return self.y_pred,self.prob_pred

  def confusion_matrix(self,y_test,y_predict):
    print('I am evaluating the performance of model with the confusion matrix\n...')
    self.cm=confusion_matrix(y_test,y_predict)
    self.group_names = ['True Negative','False Positive\n (Type I Error)','False Negative\n (Type II Error)','True Positive']
    self.group_counts = ["{0:0.0f}".format(value) for value in  self.cm.flatten()]
    self.group_percentages = ["{0:.2%}".format(value) for value in  self.cm.flatten()/np.sum(self.cm)]
    self.labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in zip(self.group_names,self.group_counts,self.group_percentages)]
    self.labels = np.asarray(self.labels).reshape(2,2)
    plt.figure(figsize=(12, 7))
    plt.suptitle("Confusion Matrix",fontsize=14,fontweight='bold',color='tab:orange')
    sns.heatmap(self.cm,center=True, annot=self.labels, fmt='', cmap='Oranges')
    plt.ylabel('Actual values',fontsize=12,fontweight='bold',color='tab:orange')
    plt.xlabel('Predicted values',fontsize=12, fontweight='bold',color='tab:orange')
    plt.show()
    return self.cm

  def AUC_ROC(self,y,prob_pred):
    print('I am evaluating the performance of model with AUC_ROC\n...')
    self.auc_roc = roc_auc_score(y,prob_pred)
    self.fpr, self.tpr, _ = roc_curve(y,prob_pred)
    plt.figure(figsize=(12, 7))
    plt.plot(self.fpr, self.tpr, marker='.', label=r'Trained Model (AUROC=%.2f %%)'%(100*self.auc_roc))
    plt.plot([0, 1], [0, 1],  'r--',label='No Skill')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.suptitle('Area Under the Receiver Operating Characteristics (AUROC)')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend()
    plt.fill_between(self.fpr, self.tpr, 0, facecolor='green', alpha=0.5)
    return self.auc_roc

  def Optimizer(self,model,params_grid,X,y): 
    print('I am searching for the optimal values of model hyperparameter \n...')
    self.clf = GridSearchCV(model, params_grid, refit = True, cv = 5, scoring = 'roc_auc', verbose=True, n_jobs=-1) 
    self.grid_result= self.clf.fit(X,y)
    self.means= self.grid_result.cv_results_['mean_test_score']
    self.stds= self.grid_result.cv_results_['std_test_score']
    self.params= self.grid_result.cv_results_['params']
    for self.mean, self.stdev, self.param in zip(self.means, self.stds, self.params):
      print("%.2f %% (%.2f) with: %r" % (100*self.mean, self.stdev, self.param))
    print("The best ROC_AUC: %.2f %% using configuration %s" % (100*self.grid_result.best_score_, self.grid_result.best_params_))
    return self.grid_result


class Logistic_Model():
  """
  This class is to train and validate the Logistic Regression. Note that, in spite of its name, 
  logistic regression is a model for classification, not regression. Indeed, 
  it is simple yet more powerful algorithm for linear and binary classification problems.
  Thus, it is one of the most widely used algorithms for classification in industry.
  """

  def __init__(self,Data_Engineering,Model_Validator):
    print('\033[1m'+'I am focusing on the Logistic model'+'\033[0m'+'\n...')
    self.z=np.arange(-7, 7, 0.1)
    self.sigmoid(self.z)
    self.X_train, self.X_test=Data_Engineering.X_train, Data_Engineering.X_test
    self.y_train, self.y_test=Data_Engineering.y_train, Data_Engineering.y_test
    self.trained_LR=self.Traintor(self.X_train,self.y_train)
    self.y_pred,self.prob_pred = Model_Validator.Predictor(self.trained_LR,self.X_test)
    self.cm=Model_Validator.confusion_matrix(self.y_test,self.y_pred)
    self.auroc=Model_Validator.AUC_ROC(self.y_test,self.prob_pred[:, 1])
    self.lr=LogisticRegression(random_state = 0)
    self.param_grid = {'penalty': ['l1', 'l2'],'C':np.logspace(-4, 4, 20)}
    self.best_logis =Model_Validator.Optimizer(self.lr,self.param_grid,self.X_train,self.y_train)
    self.y_pred,self.prob_pred = Model_Validator.Predictor(self.best_logis,self.X_test)
    self.auroc=Model_Validator.AUC_ROC(self.y_test,self.prob_pred[:, 1])

  def sigmoid(self,z):
    print('Have a look at an example of the logistic or sigmoid function below.')
    self.phi_z=1/(1+np.exp(-z))
    plt.plot(z, self.phi_z,linewidth=3,label=r'$\phi (z)=\frac{1}{1+e^{-z}}$')
    plt.axvline(0.0, color='k')
    plt.axhline(y=1, ls='dotted', color='k')
    plt.axhline(y=0.5, ls='dotted', color='k')
    plt.axhline(y=0, ls='dotted', color='k')
    plt.yticks([0.0, 0.5, 1.0])
    plt.ylim(-0.1, 1.1)
    plt.suptitle(r'The sigmoid or logistic function $\phi (z)=\frac{1}{1+e^{-z}}$')
    plt.xlabel('Net input ($z=w^{T}x$)')
    plt.ylabel('The prob. the positive event (p)')
    plt.legend()
    plt.show()

  def Traintor(self,X,y):
    print('I am training model\n...')
    self.lr=LogisticRegression(random_state = 0)
    self.lr.fit(X, y)
    return self.lr

class Support_Vector_Class():
  """
  This class is to train and validate the Support Vector Class (SVC). 
  Indeed, it is to belongs to the Support Vector Machine (SVM) and one of most popular non-linear algorithms.
  SVC creates a decision boundary which makes the distinction between two or more classes. 
  How to draw or determine the decision boundary is the most critical part in SVC algorithms. 
  When the data points in different classes are linearly separable, it is an easy task to draw a decision boundary.
  """

  def __init__(self,Data_Engineering,Model_Validator):
    print('\033[1m'+'I am focusing on the Support Vector Classifier'+'\033[0m'+'\n...')
    self.X_train, self.X_test=Data_Engineering.X_train, Data_Engineering.X_test
    self.y_train, self.y_test=Data_Engineering.y_train, Data_Engineering.y_test
    self.trained_svc=self.Traintor(self.X_train,self.y_train)
    self.y_pred,self.prob_pred=Model_Validator.Predictor(self.trained_svc,self.X_test)
    self.cm=Model_Validator.confusion_matrix(self.y_test,self.y_pred)
    self.auroc=Model_Validator.AUC_ROC(self.y_test,self.prob_pred[:, 1])
    self.svc=SVC(kernel = 'rbf',probability=True, random_state = 0)
    self.param_grid= {'C': [0.1, 1, 10, 100, 1000], 'gamma': [1, 0.1, 0.01, 0.001, 0.0001], 'kernel': ['rbf']}
    self.best_svc =Model_Validator.Optimizer(self.svc,self.param_grid,self.X_train,self.y_train)
    self.y_pred,self.prob_pred = Model_Validator.Predictor(self.best_svc,self.X_test)
    self.auroc=Model_Validator.AUC_ROC(self.y_test,self.prob_pred[:, 1])

  def Traintor(self,X,y):
    print('I am training model \n...')
    self.svc=SVC(kernel = 'rbf',probability=True, random_state = 0)
    self.svc.fit(X,y)
    return self.svc


class main():
  Data_Extraction=Data_Extraction(git_url)
  #Data_Information=Data_Information(Data_Extraction)
  Data_Engineering=Data_Engineering(Data_Extraction)
  #Model_Selector=Model_Selector(Data_Engineering)
  Model_Validator=Model_Validator()
  #Logistic_Model=Logistic_Model(Data_Engineering,Model_Validator)
  Support_Vector_Class=Support_Vector_Class(Data_Engineering,Model_Validator)

if __name__=='__main__':
  main()

"""# Useful References

https://www.kaggle.com/rishidamarla/4-different-algorithms-on-breast-cancer-dataset

https://github.com/finnqiao/bank-logistic/blob/master/bank-logistic-v2.ipynb
"""