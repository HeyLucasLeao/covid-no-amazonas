import pandas as pd
from os import listdir
import geopandas as gpd

def updating_csvs():
    PATH_CSV_NORMALIZED = r'./raspagem_dos_boletins_diarios/normalized_csvs'
    normalized_csvs = listdir(PATH_CSV_NORMALIZED)
    dici = {'leitos_clinicos_covid-19': 'Leitos Clínicos (Covid-19)',
    'leitos_clinicos_geral': 'Leitos Clínicos (Geral)',
    'sala_vermelha_covid-19': 'Sala Vermelha (Covid-19)',
    'sala_vermelha_geral': 'Sala Vermelha (Geral)',
    'uti_covid-19': 'UTI (Covid-19)',
    'uti_geral': 'UTI (Geral)'}

    ocupacao_em_hospitais = pd.DataFrame()
    for file in normalized_csvs:
        dados_normalizados = pd.read_csv(PATH_CSV_NORMALIZED + r'/' + file)
        dados_normalizados.rename(columns = {'Rede Publica': 'Rede Pública',
        'Adulto (total)':'Adulto (Total)',
        'Oncologico': 'Oncológico',
        'Cardiaco': 'Cardíaco'}, inplace=True)
        name = dici[file[:file.index('.')]]
        dados_normalizados.insert(0, column='Unidade', value=name)
        ocupacao_em_hospitais = pd.concat([ocupacao_em_hospitais, dados_normalizados])

    ocupacao_em_hospitais['Data'] = ['20' + x for x in ocupacao_em_hospitais['Data']]
    ocupacao_em_hospitais['Data'] = pd.to_datetime(ocupacao_em_hospitais['Data'])
    ocupacao_em_hospitais.fillna(0, inplace=True)

    return ocupacao_em_hospitais

def updating_df():
    df = pd.read_csv(r"./src/gzip/dados-de-covid-no-brasil.csv.gz", compression='gzip')
    df['date'] = pd.to_datetime(df['date'])
    df = df.query("city != 'TOTAL'")
    df['city'] = [x for x in df['city'] if x[:28] != 'CASO SEM LOCALIZAÇÃO DEFINIDA']
    df.sort_values('totalCases', ascending=False,inplace=True)
    return df

gjson_estados_brasileiros = gpd.read_file(r'./src/geojson/brazil-states.geojson')

def updating_total_por_estado():
    total_por_estado = pd.read_csv(r'./src/gzip/total-por-estado.csv.gz')
    dici = dict([(x,y) for x,y in zip(gjson_estados_brasileiros['sigla'], gjson_estados_brasileiros['name'])])
    total_por_estado['name'] = [dici[x] for x in total_por_estado['state']]
    return total_por_estado

def predicao():
    y_pred = pd.read_csv(r'src/pred/y_pred.csv')

    with open(r'src/pred/smape.txt', 'r+') as file:
        smape = file.read()
    return y_pred, smape