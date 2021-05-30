from shutil import Error
import pandas as pd
import datetime as dt
from os import system
from time import sleep
from subprocess import Popen
from src.model import treinando_e_prevendo

x = 0

while True:
    try:
        url = 'https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-cities.csv'
        df = pd.read_csv(url)
        data = str(dt.datetime.now())[:10] 
        df_estado = pd.read_csv(
            'https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv')
        df_estado_soma_casos = df_estado.query(
            f"state == 'AM' and date == '{data}'")['newCases'].values[0]
        soma_casos = df.query(f"state == 'AM' and last_info_date == '{data}' and city != 'CASO SEM LOCALIZAÇÃO DEFINIDA/AM'")[
            'newCases'].sum()
    except:
        x += 1
        for i in reversed(range(30)):
            print(f"Dados incompletos.")
            print(f"Tentativa nº: {x}")
            print(
                f"Tempo restante para a próxima tentativa: {i + 1} minuto(s).")
            sleep(60)
            system('cls')
        continue

    if soma_casos > 0 and df_estado_soma_casos > 0:
        try:
            print('Atualizando banco de dados do Brasil & Amazonas...')
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
            df.to_csv(r"./src/datasets/dados-de-covid-no-brasil.csv.gz", index=False, compression="gzip")
            
            url = 'https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv'
            total_por_estado = pd.read_csv(url, 
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

            total_por_estado = total_por_estado.query(f"date == '{data}' and state != 'TOTAL'")
            total_por_estado.to_csv(r'./src/datasets/total-por-estado.csv.gz', compression="gzip", index=False)
            print('Dados atualizados!')
            sleep(10)
            print('Extraindo predição...')
            y_pred, smape = treinando_e_prevendo()
            y_pred.to_csv(r'src/pred/y_pred.csv', index=False)
            with open(r'src/pred/smape.txt', 'w+', encoding='utf-8') as file:
                file.write(smape)
            print('Predição extraída com sucesso!')
            sleep(10)
            print('Atualizando CSVs de ocupação...')
            from subprocess import Popen
            Popen.wait(Popen('conda run -n covid-no-amazonas python updating.py',
             shell=True, 
             cwd=r'raspagem_dos_boletins_diarios'), 
                timeout=360)
            with open(r'push_automatico/upar_dados.py', "r") as f:
                exec(f.read())
            print("Processo finalizado.")
            sleep(10)
            break
        except Error:
            raise SystemExit(0)
    else:
        x += 1
        for i in reversed(range(30)):
            print(f"Dados incompletos.")
            print(f"Tentativa nº: {x}")
            print(
                f"Tempo restante para a próxima tentativa: {i + 1} minuto(s).")
            sleep(60)
            system('cls')
        continue
