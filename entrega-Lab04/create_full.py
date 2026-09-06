from procesar_encounters import read_encounters
from procesar_observations import read_observations
from procesar_patients import read_patients


def merge_full():
    '''
    UDF para generar dataFrame "full" que contiene el merge de los archivos patients, encounters y observations
    utiliza los .py: procesar_patients, procesar_encounters y procesar_observations
    '''
    pat = read_patients('patients.csv')
    enc = read_encounters('encounters.csv')
    obs = read_observations('observations.csv')
    full = enc.merge(
        obs,            # para corregur issue1:
        on=['patient','encounter'], # aqui meto un bug intencionalmente para corregirlo despues, deberia...
        how='left', #...ser ['patient', 'encounter'] y de esta manera se duplicara la columna patient
        validate='1:m',
        indicator=True
    )
    full = (full
        .drop(columns={'_merge'})
        .merge(
            pat,
            #left_on = 'patient_x', # al corregir el issue de arriba tambien debo cambiar aqui
            on = 'patient', # originalmente era solo on = 'patient', sin left o right
            how='left',     # para issue2 (perf)
            validate='m:1', # aqui en indicator hace que me sobre la columna _merge que no es...
            indicator=False) #...necesaria para el analisis. No es bug pero puede entrar como issue
           )
    print(full.shape)
    return full