# Este apartado será para disponer de todas las funciones requeridas para el proyecto de recursos humanos


# Librerias necesarias 
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer # Para imputación
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import cross_val_predict, cross_val_score, cross_validate
import joblib
from sklearn.preprocessing import StandardScaler # Escalar variables 
from sklearn.feature_selection import RFE


# Permite ejecutar un archivo  con extensión .sql que contenga varias consultas
def ejecutar_sql (nombre_archivo, cur):
  sql_file = open(nombre_archivo)
  sql_as_string = sql_file.read()
  sql_file.close
  cur.executescript(sql_as_string)


# Imputa variables numéricas   
def imputar_numericas (df, tipo):

    if str(tipo) == 'mean':
        numericas = df.select_dtypes(include = ['number']).columns
        imp_mean = SimpleImputer(strategy = 'mean')
        df[numericas] = imp_mean.fit_transform(df[numericas])
        return df
    
    if str(tipo) == 'most_frequent':
        numericas = df.select_dtypes(include = ['number']).columns
        imp_mean = SimpleImputer(strategy = 'most_frequent')
        df[numericas] = imp_mean.fit_transform(df[numericas])
        return df


# Imputar variables categóricas y numéricas
def imputar_f (df, list_cat):  
        
    
    df_c = df[list_cat]

    df_n = df.loc[:,~df.columns.isin(list_cat)]

    imputer_n = SimpleImputer(strategy = 'most_frequent')
    imputer_c = SimpleImputer( strategy = 'most_frequent')

    imputer_n.fit(df_n)
    imputer_c.fit(df_c)
    imputer_c.get_params()
    imputer_n.get_params()

    X_n = imputer_n.transform(df_n)
    X_c = imputer_c.transform(df_c)

    df_n = pd.DataFrame(X_n,columns = df_n.columns)
    df_c = pd.DataFrame(X_c,columns = df_c.columns)
    df_c.info()
    df_n.info()

    df = pd.concat([df_n, df_c], axis = 1)
    return df


# Selecciona modelos 
def sel_variables(modelos, X, y, threshold):
    
    var_names_ac = np.array([])
    for modelo in modelos:
        #modelo=modelos[i]
        modelo.fit(X,y)
        sel = SelectFromModel(modelo, prefit = True, threshold = threshold)
        var_names = modelo.feature_names_in_[sel.get_support()]
        var_names_ac = np.append(var_names_ac, var_names)
        var_names_ac = np.unique(var_names_ac)
    
    return var_names_ac


def medir_modelos(modelos,scoring,X,y,cv):

    metric_modelos=pd.DataFrame()
    for modelo in modelos:
        scores=cross_val_score(modelo,X,y, scoring=scoring, cv=cv )
        pdscores=pd.DataFrame(scores)
        metric_modelos=pd.concat([metric_modelos,pdscores],axis=1)
    
    metric_modelos.columns=["logistic_r","rf_classifier","sgd_classifier","xgboost_classifier"]
    return metric_modelos


# Esta función se encarga de cargar y procesar nuevos datos
def preparar_datos (df):

    # Cargar modelo y listas
    list_cat = joblib.load('Salidas\\list_cat.pkl')
    list_dummies = joblib.load('Salidas\\list_dummies.pkl')
    var_names = joblib.load('Salidas\\var_names.pkl')
    scaler = joblib.load( 'Salidas\\scaler.pkl') 

    # Recategorización de variables
    clasificador_education(df, 'EducationField')
    clasificador_jobrole(df,'JobRole')
    df.drop(['EducationField','JobRole'], axis = 1, inplace = True)

    # Ejecutar funciones de transformaciones
    df = imputar_f(df, list_cat)

    df_dummies = pd.get_dummies(df, columns = list_dummies, dtype = int)
    df_dummies = df_dummies.loc[:,~df_dummies.columns.isin(['EmployeeID'])]

    # Ordenamos las variables en el orden de entrenamiento del escalar
    df_dummies = df_dummies.reindex(['Age', 'DistanceFromHome', 'Education', 'JobLevel', 'MonthlyIncome',
       'NumCompaniesWorked', 'PercentSalaryHike', 'StockOptionLevel',
       'TotalWorkingYears', 'TrainingTimesLastYear', 'YearsAtCompany',
       'YearsSinceLastPromotion', 'YearsWithCurrManager',
       'EnvironmentSatisfaction', 'JobSatisfaction', 'WorkLifeBalance',
       'JobInvolvement', 'PerformanceRating', 'BusinessTravel_Non-Travel',
       'BusinessTravel_Travel_Frequently', 'BusinessTravel_Travel_Rarely',
       'Department_Human Resources', 'Department_Research & Development',
       'Department_Sales', 'Gender_Female', 'Gender_Male',
       'MaritalStatus_Divorced', 'MaritalStatus_Married',
       'MaritalStatus_Single', 'education_sector_Human Resources',
       'education_sector_Research','education_sector_Marketing',
       'job_rol_Research & Development', 'job_rol_Human Resources',
       'job_rol_Manager', 'job_rol_Sales'], axis = 1)

    X2 = scaler.transform(df_dummies)
    X = pd.DataFrame(X2, columns = df_dummies.columns)
    X = X[var_names]
    
    return X


def convertir_fecha(dataframe, columna):

    dataframe[columna] = pd.to_datetime(dataframe[columna])

    return dataframe.info()

def convertir_fecha(dataframe, columna):

    dataframe[columna] = pd.to_datetime(dataframe[columna])

    return dataframe.info()


def clasificador_jobrole(df, nombre_columna):
    df[nombre_columna] = df[nombre_columna].astype('category')

    # Definimos las categorías y cómo las vamos a recategorizar 
    diccionario_rol = {
        'Healthcare Representative': 'Research & Development',
        'Research Scientist': 'Research & Development',
        'Sales Executive': 'Sales',
        'Human Resources': 'Human Resources',
        'Research Director': 'Research & Development',
        'Laboratory Technician': 'Research & Development',
        'Manufacturing Director': 'Research & Development',
        'Sales Representative': 'Sales',
        'Manager': 'Manager'
    }

    # Creamos una columna nueva que contenga la recategorización 
    df["job_rol"] = df[nombre_columna].replace(diccionario_rol)

    return df

def clasificador_education(df, nombre_columna):
    df[nombre_columna] = df[nombre_columna].astype('category')

    # Definimos las categorías y cómo las vamos a recategorizar 
    diccionario_educacion = {
        'Life Sciences': 'Research',
        'Other': 'Research',
        'Medical': 'Research',
        'Technical Degree': 'Research',
        'Marketing': 'Marketing',
        'Human Resources': 'Human Resources',
    }

    # Creamos una columna nueva que contenga la recategorización 
    df["education_sector"] = df[nombre_columna].replace(diccionario_educacion)

    return df


def funcion_rfe(modelos,X,y, num_variables, paso):
  resultados = {}
  for modelo in modelos: 
    rfemodelo = RFE(modelo, n_features_to_select = num_variables, step = paso)
    fit = rfemodelo.fit(X,y)
    var_names = fit.get_feature_names_out()
    puntaje = fit.ranking_
    diccionario_importancia = {}
    nombre_modelo = modelo.__class__.__name__

    for i,j in zip(var_names,puntaje):
      diccionario_importancia[i] = j
      resultados[nombre_modelo] = diccionario_importancia
  
  return resultados
