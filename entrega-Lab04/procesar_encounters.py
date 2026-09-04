import pandas as pd

def read_encounters(file):
    '''
    UDF para leer archivo encounters.csv con dtypes especificos para optimizar memoria
    '''
    enc = pd.read_csv(file, # encounters.csv
                      dtype={'ID': 'category',
                             'PATIENT': 'category',
                             'ORGANIZATION': 'category',
                             'PROVIDER': 'category',
                             'PAYER': 'category',
                             'ENCOUNTERCLASS': 'category',
                             'CODE': 'category',
                             'DESCRIPTION': 'category',
                             'BASE_ENCOUNTER_COST': 'float32',
                             'TOTAL_CLAIM_COST': 'float32',
                             'PAYER_COVERAGE': 'float32',
                             'REASONCODE': 'float64',
                             'REASONDESCRIPTION': 'category'},
                      parse_dates=['START', 'STOP'])
    enc.columns = enc.columns.str.lower()
    enc = enc.rename(columns={'id': 'encounter',
                               'description': 'enc_desc',
                               'code': 'enc_code'})
    return enc