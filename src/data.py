from os import listdir
from statsmodels.tsa.filters.hp_filter import hpfilter
from os import listdir
import pandas as pd
import numpy as np
import geopandas as gpd

PATH_PDF = r'./raspagem_dos_boletins_diarios/relatorios'
PATH_CSV_RAW = r'./raspagem_dos_boletins_diarios/raw_csvs'
PATH_CSV_NORMALIZED = r'./raspagem_dos_boletins_diarios/normalized_csvs'

def epocas_festivas():
    epocas_festivas = pd.read_csv(r'./epocas_festivas/epocas_festivas.csv')
    epocas_festivas['date'] = ['2020-' + x for x in epocas_festivas['date'] if '2020-' not in x] #feito manualmente, necessário otimizar
    feriados_ano_atual = [(x.replace('2020-','2021-'),y) for x,y in zip(epocas_festivas['date'], epocas_festivas['name']) if '2021-' not in x]
    feriados_ano_atual = pd.DataFrame(feriados_ano_atual, columns=['date', 'name'])
    epocas_festivas = pd.concat([epocas_festivas, feriados_ano_atual], ignore_index=True)
    epocas_festivas['date'] = pd.to_datetime(epocas_festivas['date'])
    return epocas_festivas

def dados_apresentaveis(x):
    x = round(x)
    x ="{:,}".format(x)
    x = x.replace(',','.')
    return x


def to_zero(x):
    if x < 0:
        x = 0
    return x


dias_traduzidos = {'Monday': 'Segunda', 
                    'Tuesday': 'Terça',
                    'Wednesday': 'Quarta',
                    'Thursday': 'Quinta',
                    'Friday': 'Sexta',
                    'Saturday': 'Sábado',
                    'Sunday': 'Domingo'}

gjson_estados_brasileiros = gpd.read_file(r"https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson")
gjson_municipios_amazonas = gpd.read_file(r"https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-13-mun.json")
gjson_estados_brasileiros.set_index('id', inplace=True)
gjson_municipios_amazonas.set_index('id', inplace=True)

#Importar DataFrame principal

#Importar dados de Ocupação em Hospital
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
last_info = ocupacao_em_hospitais['Data'].tail(1)
last_info = str(last_info).split()[1]

url = 'https://github.com/wcota/covid19br/blob/master/cases-brazil-cities-time.csv.gz?raw=true'
df = pd.read_csv(url, compression='gzip', usecols=[
                                                    'date', 
                                                    'state', 
                                                    'city', 
                                                    'newDeaths', 
                                                    'deaths', 
                                                    'newCases', 
                                                    'totalCases', 
                                                    'deaths_per_100k_inhabitants', 
                                                    'totalCases_per_100k_inhabitants',
                                                    'deaths_by_totalCases'
                                                    ])
df['date'] = pd.to_datetime(df['date'])
df = df.query("city != 'TOTAL'")
df['city'] = [x for x in df['city'] if x[:28] != 'CASO SEM LOCALIZAÇÃO DEFINIDA']
df.sort_values('totalCases', ascending=False,inplace=True)

#Var1
total_de_casos_amazonas = df.query("state == 'AM'").groupby('date').sum()
total_de_casos_amazonas.reset_index(inplace=True)
total_de_casos_amazonas['dia_da_semana'] = total_de_casos_amazonas['date'].dt.day_name()
total_de_casos_amazonas['dia_da_semana'] = total_de_casos_amazonas['dia_da_semana'].map(dias_traduzidos)
total_de_casos_amazonas['media_movel_novos_casos'] = total_de_casos_amazonas['newCases'].ewm(span=7).mean().round()
total_de_casos_amazonas['media_movel_novos_casos'].fillna(value=0, inplace=True)

#Var2
total_de_casos_amazonas_por_mes = total_de_casos_amazonas.set_index('date').groupby(pd.Grouper(freq='M')).sum()[['newDeaths','newCases']]
total_de_casos_amazonas_por_mes.reset_index(inplace=True)
total_de_casos_amazonas_por_mes['taxa_de_letalidade'] = round(total_de_casos_amazonas_por_mes['newDeaths']/total_de_casos_amazonas_por_mes['newCases'] * 100, 2)

#Var3
total_por_estado = pd.read_csv('https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv', 
                               usecols=[
                                   'date', 
                                   'state', 
                                   'city', 
                                   'newDeaths', 
                                   'deaths',
                                   'newCases', 
                                   'totalCases', 
                                   'deaths_per_100k_inhabitants', 
                                   'totalCases_per_100k_inhabitants',
                                   'deaths_by_totalCases',  'vaccinated',
                                   'vaccinated_per_100k_inhabitants'
                                       ]
                              )

if df[df['state'] == 'AM']['newCases'].head(1).values <= 0:
    df.drop(df.head(1).index, inplace=True)
if total_por_estado[total_por_estado['state'] == 'AM']['newCases'].tail(1).values <= 0:
    total_por_estado.drop(total_por_estado.tail(1).index, inplace=True)

total_por_estado = total_por_estado.query(f"date == '{last_info}' and state != 'TOTAL'")
dici = dict([(x,y) for x,y in zip(gjson_estados_brasileiros['sigla'], gjson_estados_brasileiros['name'])])
total_por_estado['name'] = [dici[x] for x in total_por_estado['state']]

#Var4
tabela_de_epocas_festivas_com_dados = epocas_festivas()
tabela_de_epocas_festivas_com_dados = pd.merge(tabela_de_epocas_festivas_com_dados, 
                           total_de_casos_amazonas[['date','newCases', 'newDeaths']], 
                           on='date',
                           how='left').sort_values('date').dropna().reset_index()

#Var5
total_gjson_por_estado = total_por_estado
total_gjson_por_estado.reset_index(inplace=True)
total_gjson_por_estado['id'] = [(i + 1) for i in range(len(total_gjson_por_estado['state']))]

total_gjson_por_municipio = df.query("state == 'AM' and city != 'CASO SEM LOCALIZAÇÃO DEFINIDA/AM'")
total_gjson_por_municipio = total_gjson_por_municipio.query(f"date == '{last_info}'")
dici = dict([(x,y) for x,y in zip(gjson_municipios_amazonas.name, gjson_municipios_amazonas.index)])
total_gjson_por_municipio['city'] = [x[:x.index('/')] for x in total_gjson_por_municipio['city']]
total_gjson_por_municipio['id'] = [dici[x] for x in total_gjson_por_municipio['city']]

#Var6
total_10_maiores_cidades = df.groupby('city').max().sort_values('totalCases', ascending=False).head(10)
total_10_maiores_cidades.reset_index(inplace=True)
total_10_maiores_cidades.sort_values('city', inplace=True)

#Var7
total_de_casos_amazonas['crescimento_novos_casos'] = (total_de_casos_amazonas['newCases'].diff() / total_de_casos_amazonas['newCases'].rolling(7).mean()) * 100
total_de_casos_amazonas['crescimento_novos_obitos'] = (total_de_casos_amazonas['newDeaths'].diff() / total_de_casos_amazonas['newCases'].rolling(7).mean()) * 100
crescimento_percentual = pd.merge(total_de_casos_amazonas[['date','crescimento_novos_casos']], 
                                  total_de_casos_amazonas[['date', 'crescimento_novos_obitos']], 
                                  on='date', how='left')

crescimento_de_casos = crescimento_percentual[['date', 'crescimento_novos_casos']]
crescimento_de_casos.insert(1,column= 'variavel',value='crescimento_novos_casos')
crescimento_de_casos.rename(columns={'crescimento_novos_casos': 'valor'}, inplace=True)
crescimento_de_obitos = crescimento_percentual[['date', 'crescimento_novos_obitos']]
crescimento_de_obitos.insert(1,column= 'variavel',value='crescimento_novos_obitos')
crescimento_de_obitos.rename(columns={'crescimento_novos_obitos': 'valor'}, inplace=True)
crescimento = pd.concat([crescimento_de_casos, crescimento_de_obitos])
crescimento.sort_values(['date','variavel'], inplace=True)
dici = {'crescimento_novos_obitos': "Óbitos", 'crescimento_novos_casos': 'Casos'}
crescimento['variavel'] = crescimento['variavel'].apply(lambda x: dici[x])

#Var8
media_casos_por_dia_da_semana = total_de_casos_amazonas.groupby('dia_da_semana')[['newCases', 'newDeaths', 'crescimento_novos_casos']].mean().round().reindex(['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'])
media_casos_por_dia_da_semana['newDeaths'] = [round(x) for x in media_casos_por_dia_da_semana['newDeaths']]
media_casos_por_dia_da_semana['newCases'] = [round(x) for x in media_casos_por_dia_da_semana['newCases']]
media_casos_por_dia_da_semana['crescimento_novos_casos'] = [round(x) for x in media_casos_por_dia_da_semana['crescimento_novos_casos']]
media_casos_por_dia_da_semana.rename(columns={'newDeaths': 'Novos Óbitos',
                                             'newCases': 'Novos Casos',
                                             'crescimento': 'Crescimento'}, inplace=True)
media_casos_por_dia_da_semana.rename_axis('Dia da Semana', inplace=True)

#Var9
_, tendencia_de_novos_casos = hpfilter(total_de_casos_amazonas['newCases'])
tendencia_de_novos_casos = tendencia_de_novos_casos.apply(to_zero)
_, tendencia_de_novas_mortes = hpfilter(total_de_casos_amazonas['newDeaths'])
tendencia_de_novas_mortes = tendencia_de_novas_mortes.apply(to_zero).round()

#Var10
ranking_nacional = total_por_estado[['state', 'newDeaths', 'deaths', 'newCases',	'totalCases', 'deaths_per_100k_inhabitants', 'totalCases_per_100k_inhabitants', 'vaccinated',	'vaccinated_per_100k_inhabitants', 'name']]
ranking_nacional.set_index('state', inplace=True)
ranking_nacional.sort_values('deaths_per_100k_inhabitants', ascending=False, inplace=True)
ranking_nacional['newCases'] = ranking_nacional['newCases'].apply(dados_apresentaveis)
ranking_nacional['newDeaths'] = ranking_nacional['newDeaths'].apply(dados_apresentaveis)
ranking_nacional['deaths'] = ranking_nacional['deaths'].apply(dados_apresentaveis)
ranking_nacional['totalCases'] = ranking_nacional['totalCases'].apply(dados_apresentaveis)
ranking_nacional['totalCases_per_100k_inhabitants'] = ranking_nacional['totalCases_per_100k_inhabitants'].apply(dados_apresentaveis)
ranking_nacional['deaths_per_100k_inhabitants'] = ranking_nacional['deaths_per_100k_inhabitants'].apply(dados_apresentaveis)
ranking_nacional['vaccinated'] = ranking_nacional['vaccinated'].apply(dados_apresentaveis)
ranking_nacional['vaccinated_per_100k_inhabitants'] = ranking_nacional['vaccinated_per_100k_inhabitants'].apply(dados_apresentaveis)
ranking_nacional.reset_index(inplace=True)
ranking_nacional = ranking_nacional.rename(columns={'name': 'Estado',
                                                                'state': 'Sigla', 
                                                                'deaths': "Total de Óbitos", 
                                                                'totalCases': 'Total de Casos', 
                                                                'deaths_per_100k_inhabitants': 
                                                                'Óbitos por 100k Habitantes', 
                                                                'totalCases_per_100k_inhabitants': 
                                                                'Total de Casos por 100k Habitantes', 
                                                                'newCases': 'Novos Casos', 
                                                                'newDeaths': 'Novos Óbitos', 
                                                                'vaccinated': "Vacinados", 
                                                                'vaccinated_per_100k_inhabitants': "Vacinados por 100k Habitantes"})
ranking_nacional.index = np.arange(1, len(ranking_nacional) + 1)
ranking_nacional = ranking_nacional[['Estado', 
                                                'Sigla', 
                                                'Novos Casos', 
                                                'Novos Óbitos', 
                                                'Total de Casos', 
                                                'Total de Óbitos', 
                                                'Total de Casos por 100k Habitantes', 
                                                'Óbitos por 100k Habitantes', 
                                                'Vacinados', 
                                                'Vacinados por 100k Habitantes']]
ranking_nacional.drop(columns=['Novos Casos', 'Novos Óbitos', 'Total de Casos'], axis=1, inplace=True)


#Var11
ranking_municipal = df.query(f"state == 'AM' and city != 'CASO SEM LOCALIZAÇÃO DEFINIDA/AM' and date == '{last_info}'")
ranking_municipal = ranking_municipal[['city', 'newDeaths', 'deaths', 'deaths_per_100k_inhabitants', 'totalCases_per_100k_inhabitants', 'deaths_by_totalCases']]
ranking_municipal['city'] = [x[:x.index('/')] for x in ranking_municipal['city']]
ranking_municipal['newDeaths'] = ranking_municipal['newDeaths'].apply(dados_apresentaveis)
ranking_municipal['deaths'] = ranking_municipal['deaths'].apply(dados_apresentaveis)
ranking_municipal['deaths_per_100k_inhabitants'] = ranking_municipal['deaths_per_100k_inhabitants'].apply(dados_apresentaveis)
ranking_municipal['totalCases_per_100k_inhabitants'] = ranking_municipal['totalCases_per_100k_inhabitants'].apply(dados_apresentaveis)
ranking_municipal['deaths_by_totalCases'] = ranking_municipal['deaths_by_totalCases'].apply(lambda x: x * 100)
ranking_municipal['deaths_by_totalCases'] = ranking_municipal['deaths_by_totalCases'].apply(lambda x: round(x, 2))
ranking_municipal['deaths_by_totalCases'] = ranking_municipal['deaths_by_totalCases'].apply(lambda x: "{:,.2f}".format(x))
ranking_municipal['deaths_by_totalCases'] = ranking_municipal['deaths_by_totalCases'].apply(lambda x: x + " %")
ranking_municipal['deaths_by_totalCases'] = ranking_municipal['deaths_by_totalCases'].apply(lambda x: x.replace('.', ','))
ranking_municipal.sort_values('deaths_by_totalCases', inplace=True, ascending=False)
ranking_municipal.drop('newDeaths', axis=1, inplace=True)
ranking_municipal.rename(columns={
'city': 'Cidade', 
'deaths': 'Total de Óbitos', 
'deaths_per_100k_inhabitants': 'Óbitos por 100k Habitantes', 
'totalCases_per_100k_inhabitants': 'Total de Casos por 100k Habitantes',
'deaths_by_totalCases': 'Percentual de Óbitos por Total de Casos'}, inplace=True)
ranking_municipal.index = np.arange(1, len(ranking_municipal) + 1)

#Var 12
total_de_casos_brasil = df.groupby('date').sum()
total_de_casos_brasil.reset_index(inplace=True)