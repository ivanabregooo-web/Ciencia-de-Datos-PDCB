import pandas as pd

def read_patients(file):
    '''
    UDF para leer archivo patients.csv con dtypes especificos para optimizar memoria
    '''
    cols = ['Id',
            'BIRTHDATE',
            'DEATHDATE',
            'SSN',
            'RACE',
            'ETHNICITY',
            'GENDER',
            'BIRTHPLACE',
            'LAT',
            'LON',
            'HEALTHCARE_EXPENSES',
            'HEALTHCARE_COVERAGE']
    pat = (pd.read_csv(file, # patients.csv
                      usecols=cols,
                      dtype={
                      'ID': 'category',
                      'BIRTHPLACE': 'category',
                      'RACE': 'category',
                      'ETHNICITY': 'category',
                      'GENDER': 'category',
                      'LAT': 'float32',
                      'LON': 'float32',
                      'HEALTHCARE_EXPENSES': 'float32',
                      'HEALTHCARE_COVERAGE': 'float32',
                      'SSN': 'string'},
                      parse_dates=['BIRTHDATE', 'DEATHDATE'])
                      )
    pat.columns = pat.columns.str.lower()
    pat = (pat
           .assign(ssn=pat.ssn.str.replace('-', '', regex=False).astype('int32'))
           .rename(columns={'id': 'patient'}) # para igualar el nombre de las columnas)
            )
    return pat