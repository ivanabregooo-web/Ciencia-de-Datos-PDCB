import pandas as pd


def read_observations(file):
    '''
    UDF para leer archivo observations.csv con dtypes especificos para optimizar memoria
    '''
    obs = pd.read_csv(file, #'observations.csv',
                      dtype={'PATIENT': 'category',
                             'ENCOUNTER': 'category',
                             'DESCRIPTION': 'category',
                             'VALUE': 'string',
                             'UNITS': 'string',
                             'CODE': 'category',
                             'TYPE': 'category'},
                      parse_dates=['DATE'])
    obs.columns = obs.columns.str.lower()
    obs = (obs
           .assign(units=obs.units.fillna('other').astype('category'),
                   num_val=pd.to_numeric(obs['value'], errors='coerce').astype('float32'),
                   non_num_val=lambda df: df['value'].where(df['units'] == 'other', None).astype('category'))
           .drop(columns=['type', 'value'])
           .rename(columns={'description': 'obs_desc',
                            'code': 'obs_code'})
           )
    return obs