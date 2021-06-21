import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from src.functions import *

import warnings
warnings.filterwarnings("ignore")
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
rgb = 'rgb(34, 34, 34)'
line_color = '#d9d9d9'
GLOBAL_TEMPLATE = 'plotly_dark'
MAPBOX_TOKEN = 'pk.eyJ1IjoiaGV5bHVjYXNsZWFvIiwiYSI6ImNrcDRqeW1yNzAzaHIycHNiZWo1bHBqeGkifQ.kw4Buc12S2g1CTZ7KhXwYA'

def show_grafico_de_dispersao():
    df = updating_df()

    df = df.groupby('city').max().sort_values('totalCases', ascending=False).head(10)
    df.reset_index(inplace=True)
    df.sort_values('city', inplace=True)

    total_por_estado = updating_total_por_estado()

    fig = make_subplots(subplot_titles=('10 Cidades com os Maiores Casos & Óbitos Registrados por COVID-19', 
                                        'Relação de Casos & Óbitos por 100k Habitantes por Estado'),
                        rows=1, cols=2)

    ### Configuração de gráfico a esquerda
    fig.add_trace(go.Scatter(x = df['city'], 
                             y= df['totalCases'],
                             mode='markers',
                     marker=dict(color = df['totalCases'],
                                colorscale= ['cyan', 'crimson'],
                                size=df['totalCases'],
                                sizemode='area',
                                sizeref=110,
                                showscale=False),
                             text=df['deaths'],
                             name='',
                            hovertemplate='<br>%{x}<br>' + 
                             '<br>N.º de Casos: %{y:,2f}<br>' + 
                             'N.º de Óbitos: %{text:,2f}<br>' +
                            'Data: %{customdata}'), row=1, col=1) 

    fig.update_xaxes(title_text='Cidades', row=1, col=1)
    fig.update_yaxes(title_text='N.º de Casos', row=1, col=1)
    fig['data'][0]['showlegend']=False

    ### Configuração de gráfico a direita

    for col in total_por_estado['state'].values:
        df = total_por_estado[total_por_estado['state'] == col]
        fig.add_trace(go.Scatter(x = df['totalCases_per_100k_inhabitants'], 
                     y = df['deaths_per_100k_inhabitants'], 
                     mode='markers',
                    name=df['name'].values[0],
                    marker=dict(
                                size=df['totalCases'],
                                sizemode='area',
                                sizeref=80*5,
                                showscale=False,
                               opacity=0.50),
                    text=df['name'],
                    customdata=df[['totalCases', 'deaths']],
                    hoverlabel=dict(namelength=0),
                    hovertemplate='<br>%{text}<br>' + 
                    '<br>Casos por 100k Habitantes: %{x:,f}<br>' + 
                    'Óbitos por 100k Habitantes: %{y:,f}' +
                    '<br>N.º de Casos: %{customdata[0]:,2f}' + 
                    '<br>N.º de Óbitos: %{customdata[1]:,2f}<br>'), row=1, col=2)

    fig.update_yaxes(type="log", row=1,col=2)

    fig.update_traces(marker=dict(color='#597386'), row=1, col=2)

    fig.update_xaxes(title_text='Óbitos por 100k Habitantes', row=1, col=2)
    fig.update_yaxes(title_text='Casos por 100k Habitantes', row=1, col=2)

    ###Global

    fig.update_layout(height = 800, width = 1600, separators=",.", font=dict(size=12), template=GLOBAL_TEMPLATE, paper_bgcolor=rgb, plot_bgcolor=rgb)
    
    return fig


def show_mapa_nacional():
    gjson_estados_brasileiros = gpd.read_file(r'src/geojson/brasil.geojson')
    gjson_municipios_amazonas = gpd.read_file(r'src/geojson/amazonas.json')
    gjson_estados_brasileiros.set_index('id', inplace=True)
    gjson_municipios_amazonas.set_index('id', inplace=True)

    total_por_estado = updating_total_por_estado()
    total_gjson_por_estado = total_por_estado
    total_gjson_por_estado.reset_index(inplace=True)
    total_gjson_por_estado['id'] = [(i + 1) for i in range(len(total_gjson_por_estado['state']))]

    df = updating_df()

    total_gjson_por_municipio = df.query("state == 'AM' and city != 'CASO SEM LOCALIZAÇÃO DEFINIDA/AM'")
    total_gjson_por_municipio = total_gjson_por_municipio.query(f"date == date.max()")
    dici = dict([(x,y) for x,y in zip(gjson_municipios_amazonas.name, gjson_municipios_amazonas.index)])
    total_gjson_por_municipio['city'] = [x[:x.index('/')] for x in total_gjson_por_municipio['city']]
    total_gjson_por_municipio['id'] = [dici[x] for x in total_gjson_por_municipio['city']]

    fig = px.choropleth_mapbox(data_frame=total_gjson_por_estado, 
                               locations= 'id', 
                               geojson=gjson_estados_brasileiros, 
                               color = 'deaths', 
                               hover_name = 'name',
                               hover_data={'id': False, 'newCases': ":,2f", 'totalCases': ":,2f", 'newDeaths': ":2,f", 'deaths': ":,2f"}, 
                               center={'lat': -15, 'lon':-54}, 
                               zoom = 3.35, 
                               mapbox_style="carto-positron", 
                               color_continuous_scale=px.colors.sequential.Reds, 
                               opacity = 0.95,
                               labels={"totalCases": "N.º de Casos", "city": "Cidade", "deaths": "N.º de Óbitos", "newCases": "Novos Casos", "newDeaths": "Novos Óbitos"})

    fig.update_layout(width=800, height=800, separators=",.", template=GLOBAL_TEMPLATE, paper_bgcolor=rgb, plot_bgcolor=rgb)
    fig.update_layout(mapbox_style="dark", mapbox_accesstoken=MAPBOX_TOKEN)
    fig.update_coloraxes(showscale=False)
    return fig


def show_mapa_municipal():
    gjson_estados_brasileiros = gpd.read_file(r'src/geojson/brasil.geojson')
    gjson_municipios_amazonas = gpd.read_file(r'src/geojson/amazonas.json')
    gjson_estados_brasileiros.set_index('id', inplace=True)
    gjson_municipios_amazonas.set_index('id', inplace=True)

    total_gjson_por_estado = updating_total_por_estado()
    total_gjson_por_estado.reset_index(inplace=True)
    total_gjson_por_estado['id'] = [(i + 1) for i in range(len(total_gjson_por_estado['state']))]

    df = updating_df()

    total_gjson_por_municipio = df.query("state == 'AM' and city != 'CASO SEM LOCALIZAÇÃO DEFINIDA/AM'")
    total_gjson_por_municipio = total_gjson_por_municipio.query(f"date == date.max()")
    dici = dict([(x,y) for x,y in zip(gjson_municipios_amazonas.name, gjson_municipios_amazonas.index)])
    total_gjson_por_municipio['city'] = [x[:x.index('/')] for x in total_gjson_por_municipio['city']]
    total_gjson_por_municipio['id'] = [dici[x] for x in total_gjson_por_municipio['city']]

    fig = px.choropleth_mapbox(data_frame=total_gjson_por_municipio, 
                               locations= 'id', 
                               geojson=gjson_municipios_amazonas, 
                               color = 'deaths', 
                               hover_name = 'city',
                               hover_data={'id': False, 
                                           'newCases': ":,2f", 
                                           'totalCases': ":,2f", 
                                           'newDeaths': ":,2f", 
                                           'deaths': ":,2f"}, 
                               center={'lat': -5, 'lon':-65}, 
                               zoom = 4.60, 
                               mapbox_style="carto-positron",
                               range_color=(0, 500),
                               color_continuous_scale=px.colors.sequential.YlOrRd, 
                               opacity = 0.95,
                               labels={"totalCases": "N.º de Casos", 
                                       "city": "Cidade", 
                                       "deaths": "N.º de Óbitos", 
                                       "newCases": "Novos Casos", 
                                       "newDeaths": "Novos Óbitos"})

    fig.update_coloraxes(showscale=False)
    fig.update_layout(mapbox_style="dark", mapbox_accesstoken=MAPBOX_TOKEN)
    fig.update_layout(width=800, height=800, separators=",.", template=GLOBAL_TEMPLATE, paper_bgcolor=rgb, plot_bgcolor=rgb)
    
    return fig

def show_dados_mensais():

    df = updating_df()
    total_de_casos_amazonas = updating_total_de_casos_amazonas(df)
    #Var2
    total_de_casos_amazonas_por_mes = total_de_casos_amazonas.set_index('date').groupby(pd.Grouper(freq='M')).sum()[['newDeaths','newCases']]
    total_de_casos_amazonas_por_mes.reset_index(inplace=True)
    total_de_casos_amazonas_por_mes['taxa_de_letalidade'] = round(total_de_casos_amazonas_por_mes['newDeaths']/total_de_casos_amazonas_por_mes['newCases'] * 100, 2)

    fig = make_subplots(subplot_titles=('Casos & Óbitos',
                                       'Taxa de letalidade (CFR)'), 
                        rows=1, cols=2)
    
    fig.add_trace(go.Bar(
                 x=total_de_casos_amazonas_por_mes['date'], 
                 y=total_de_casos_amazonas_por_mes['newCases'], 
                marker=dict(color=total_de_casos_amazonas_por_mes['newDeaths'],
                           colorscale=px.colors.sequential.Reds),
                text=total_de_casos_amazonas_por_mes['newDeaths'],
                hovertemplate=
                             '<br>N.º de Casos: %{y:,2f}<br>' + 
                             'N.º de Óbitos: %{text:,2f}<br>',
                name=''
    ), row=1, col=1)


    fig.update_yaxes(title_text='N.º de Casos', row=1, col=1)

    
    ###Gráfico a direita
    
    fig.add_trace(go.Bar(
                name='',
                 x=total_de_casos_amazonas_por_mes['date'], 
                 y=total_de_casos_amazonas_por_mes['taxa_de_letalidade'], 
                marker=dict(color=total_de_casos_amazonas_por_mes['taxa_de_letalidade'],
                colorscale=px.colors.sequential.Brwnyl),
                hovertemplate=
                             '<br>N.º de Casos: %{text:,2f}<br>' + 
                             'N.º de Óbitos: %{customdata:,2f}<br>',
                customdata=total_de_casos_amazonas_por_mes['newDeaths'],
                text=total_de_casos_amazonas_por_mes['newCases']
    ), row=1, col=2)
    
    fig.update_traces(texttemplate="%{y} %", textposition= 'outside', row=1, col=2)
    fig.update_yaxes(title_text='Percentual (%)', row=1, col=2)
    
    ###Global
    
    fig.update_layout(separators=",.",
                      height= 800, 
                      width = 1600, 

                    hovermode='x',
                     showlegend=False,
                     template=GLOBAL_TEMPLATE,
                     paper_bgcolor=rgb,
                    plot_bgcolor=rgb)
    
    fig.update_xaxes(title_text='Data', 
                     tickformat= '%y/%m/%d',           
                     tickvals=dias(),     
                     ticktext=meses_anos('2020-03-31'))
    return fig


def show_quadro_evolutivo():
    df = updating_df()
    total_de_casos_amazonas = updating_total_de_casos_amazonas(df)
    total_de_casos_brasil = df.groupby('date').sum()
    total_de_casos_brasil.reset_index(inplace=True)

    fig = make_subplots(subplot_titles=('Brasil',
                                       'Amazonas'),
                        rows=1, 
                        cols=2)

    ##Gráfico a esquerda
    fig.add_trace(go.Bar(x=total_de_casos_brasil['date'], 
                     y=total_de_casos_brasil['totalCases'],
                                 text=total_de_casos_brasil['deaths'],
                                 name='',
                                 customdata=total_de_casos_brasil[['newCases', 'newDeaths']],
                                hovertemplate=
                                 '<br>N.º de Casos: %{y:,2f}<br>' + 
                                 'N.º de Óbitos: %{text:,2f}<br>' +
                                'Novos Casos: %{customdata[0]}<br>' + 
                                'Novos Óbitos: %{customdata[1]}'), row=1, col=1)

    ##Gráfico a direita
    fig.add_trace(go.Bar(x=total_de_casos_amazonas['date'], 
                     y=total_de_casos_amazonas['totalCases'],
                                 text=total_de_casos_amazonas['deaths'],
                                 name='',
                                 customdata=total_de_casos_amazonas[['newCases', 'newDeaths']],
                                hovertemplate=
                                 '<br>N.º de Casos: %{y:,2f}<br>' + 
                                 'N.º de Óbitos: %{text:,2f}<br>' +
                                'Novos Casos: %{customdata[0]}<br>' + 
                                'Novos Óbitos: %{customdata[1]}'), row=1, col=2)
    
    #Global
    fig.update_layout(
                        height= 800, 
                        width = 1600, 
                        separators=",.", 
                        hovermode='x',
                        template=GLOBAL_TEMPLATE,
                        paper_bgcolor=rgb,
                        plot_bgcolor=rgb)

    fig.update_traces(marker=dict(color='#597386'), showlegend=False)

    fig.update_xaxes(title_text='Data',
                     tickformat= '%y/%m/%d',   
                     tickvals=dias(),   
                     ticktext=meses_anos('2020-04-01'))
    fig.update_yaxes(title_text='N.º de Casos')
    return fig

def show_dados_diarios_casos_e_obitos():
    df = updating_df()
    total_de_casos_amazonas = updating_total_de_casos_amazonas(df)
    tendencia_de_novos_casos, tendencia_de_novas_mortes = updating_tendencias(total_de_casos_amazonas)
    tabela_de_epocas_festivas_com_dados = epocas_festivas_com_dados(total_de_casos_amazonas)

    fig = px.bar(data_frame=total_de_casos_amazonas, 
                 x='date', 
                 y='newCases', 
                 hover_data={"newCases": ":,2f", 'newDeaths': ":,2f",'date': False}, 
                 labels={"newCases": "Novos Casos", "date": 'Data', 'newDeaths': 'Novos Óbitos'}, 
                 color_discrete_sequence=['#804545'])

    fig.add_trace(go.Scatter(x=total_de_casos_amazonas['date'],
                             y=tendencia_de_novos_casos.round(), 
                             line=dict(color=line_color, width=1), 
                             name="Holt-Winters (SEHW) - Casos",
                             mode='lines', 
                             hoverinfo="y", 
                             showlegend=False, 
                             hovertemplate="%{y}",
                             opacity=0.50))


    fig.add_trace(go.Scatter(x=total_de_casos_amazonas['date'], 
                             y=tendencia_de_novas_mortes, 
                             line=dict(color=line_color, width=1, smoothing=0.25), 
                             name="Holt-Winters (SEHW) - Óbitos",
                             mode='lines',
                             hoverinfo='y' , 
                             showlegend=False, 
                             hovertemplate="%{y}",
                             opacity=0.50))

    fig.add_trace(go.Scatter(x=tabela_de_epocas_festivas_com_dados['date'], 
                             y=tabela_de_epocas_festivas_com_dados['newCases'], 
                             line=dict(color='darkcyan', width=0.01),  
                             hovertemplate=tabela_de_epocas_festivas_com_dados['name'],
                             mode='markers',
                             showlegend=False,
                            name='Feriado'))

    fig.update_layout(height= 800, 
                      width = 1600, 
                      separators=",.", 
                      paper_bgcolor=rgb,
                        plot_bgcolor=rgb,
                      xaxis=dict(tickformat= '%y/%m/%d', 
                                 tickvals=dias(), 
                                 ticktext=meses_anos('2020-04-01')))

    fig.update_layout(hovermode='x', template=GLOBAL_TEMPLATE)
    
    return fig


def show_dados_diarios_obitos():
    df = updating_df()
    total_de_casos_amazonas = updating_total_de_casos_amazonas(df)
    _, tendencia_de_novas_mortes = updating_tendencias(total_de_casos_amazonas)
    tabela_de_epocas_festivas_com_dados = epocas_festivas_com_dados(total_de_casos_amazonas)

    fig = px.bar(data_frame = total_de_casos_amazonas, 
    x='date', 
    y='newDeaths', 
    labels={'newDeaths': 'Óbitos', 'date': 'Data'},
    color_discrete_sequence=['#804545'])

    fig.update_traces(hovertemplate="%{y}", name='Óbitos')
    fig.add_trace(go.Scatter(x=total_de_casos_amazonas['date'], 
                             y=tendencia_de_novas_mortes, 
                             line=dict(color=line_color, width=1), 
                             name="Holt-Winters (SEHW) - Óbitos",
                             mode='lines',
                             hoverinfo='y' , 
                             showlegend=False, 
                             hovertemplate="%{y}",
                             line_shape= 'spline'))

    fig.add_trace(go.Scatter(x=tabela_de_epocas_festivas_com_dados['date'], 
                             y=tabela_de_epocas_festivas_com_dados['newDeaths'], 
                             line=dict(color='darkcyan', width=0.01),  
                             hovertemplate=tabela_de_epocas_festivas_com_dados['name'],
                             mode='markers',
                             showlegend=False,
                            name='Feriado'))

    fig.update_layout(template=GLOBAL_TEMPLATE,
                        height= 800, 
                      width = 1600, 
                      hovermode='x',
                      separators=",.", 
                      xaxis=dict(tickformat= '%y/%m/%d', 
                                 tickvals=dias(), 
                                 ticktext=meses_anos('2020-04-01')),
                                paper_bgcolor=rgb,
                                plot_bgcolor=rgb)
    return fig



def show_crescimento():    
    df = updating_df()
    total__de_casos_amazonas = updating_total_de_casos_amazonas(df)
    crescimento, _ = updating_crescimento(total__de_casos_amazonas)
    ###Criação de Gráfico
    fig = px.bar(crescimento, 
                  y='valor',
                  x=crescimento.index, 
                  color = 'valor',
                  labels = {'valor': 'Percentual (%)', 'date': 'Data', 'percentual': "Percentual (%)"},
                color_continuous_scale=["#675067","#60748C","#50999F","#60BC9A","#9DD986","#F1ED77"],
                width=1600, height=800,facet_row='variavel')


    fig.update_traces(hovertemplate="%{y:.2f} %")
    fig.update_layout(hovermode='x', 
                      separators=",.",
                      template=GLOBAL_TEMPLATE,
                      paper_bgcolor=rgb,
                     plot_bgcolor=rgb)

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))

    fig.add_hline(y=0)
    
    
    tickvals, ticktext = traduzir_eixo_x(crescimento.index, 0, 60)
    
    ticktext = [x[:-4] for x in ticktext]
    
    fig.update_xaxes(tickformat= '%y/%m/%d', 
                     tickvals=tickvals, 
                     ticktext=ticktext,
                     tickangle=35)
    fig.update_yaxes(matches=None)
    fig.update_xaxes(showticklabels=True)
    fig.update_coloraxes(showscale=False)
    return fig



def show_dia_da_semana():
    df = updating_df()
    total__de_casos_amazonas = updating_total_de_casos_amazonas(df)
    _, media_casos_por_dia_da_semana = updating_crescimento(total__de_casos_amazonas)

    fig = px.bar(media_casos_por_dia_da_semana, 
                 y='Novos Casos', 
                 x=media_casos_por_dia_da_semana.index, 
                 color=media_casos_por_dia_da_semana.index, 
                 width= 400)

    fig.update_layout(template=GLOBAL_TEMPLATE,
                      width = 470, 
                      height=600,
                      separators=",.", 
                      xaxis={'tickangle': 35}, 
                      font=dict(size=11),
                     hovermode='x',
                     paper_bgcolor=rgb,
                     plot_bgcolor=rgb)

    fig.update_traces(hovertemplate="%{y}")
    
    return fig

def show_ocupacao_em_hospitais():
    ocupacao_em_hospitais = updating_ocupacao_em_hospitais()

    fig = px.line(data_frame=ocupacao_em_hospitais,
              x='Data',
              y=ocupacao_em_hospitais.columns[2:],
              facet_row=ocupacao_em_hospitais['Unidade'],
             height=1600, 
              width= 1600,
             labels={'value': 'Porcentagem (%)',
                    'Rede Publica': 'Rede Pública',
                    'Oncologico': 'Oncológico',
                    'Cardiaco': 'Cardíaco',
                    'variable': 'Setor'})


    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1], textangle=45))

    fig.update_layout(hovermode='x', template=GLOBAL_TEMPLATE, paper_bgcolor=rgb, plot_bgcolor=rgb, separators=",.")

    fig.update_traces(hovertemplate="%{y:.2%}")

    fig.update_xaxes(showticklabels=True)
    fig.update_yaxes(matches=None)
    
    tickvals, ticktext = traduzir_eixo_x(ocupacao_em_hospitais['Data'], 0, 14)
    
    ticktext = [x[:-4] for x in ticktext]
    
    fig.update_xaxes(tickformat= '%y/%m/%d', 
                     tickvals=tickvals, 
                     ticktext=ticktext,
                    tickangle=35)
    return fig

def show_predicao():
    df = updating_df()
    total_de_casos_amazonas = updating_total_de_casos_amazonas(df)
    tendencia_de_novos_casos, _ = updating_tendencias(total_de_casos_amazonas)

    y_pred = pd.read_csv(r'src/pred/y_pred.csv')
    
    fig = go.Figure()
    
    
    fig.add_trace(go.Bar(
                 x=total_de_casos_amazonas['date'].tail(30), 
                 y=total_de_casos_amazonas['newCases'].tail(30),
                hoverinfo='skip'))

    fig.update_traces(marker_color='gray')

    fig.add_trace(go.Scatter(x=total_de_casos_amazonas['date'].tail(30),
                             y=tendencia_de_novos_casos.round().tail(30), 
                             line=dict(color='#804545', width=1), 
                             name="Holt-Winters (SEHW) - Casos",
                             mode='lines', 
                             hoverinfo="y", 
                             showlegend=False, 
                             hovertemplate="%{y}",
                             fillcolor='Gray'))

    fig.add_trace(go.Scatter(x=y_pred['index'], 
                             y=y_pred['0'], 
                             line=dict(color='#804545', width=1), 
                             name=f"Predição por LightGBM",
                             mode='lines+markers',
                             hoverinfo='y' , 
                             showlegend=False, 
                             hovertemplate="%{y}",
                             opacity= 0.75))

    fig.update_layout(template=GLOBAL_TEMPLATE,
                    showlegend=False,
                    hovermode='x',
                      height= 400, 
                      width = 800, 
                      separators=",.", 
                        font=dict(size=11),
                     paper_bgcolor=rgb,
                     plot_bgcolor=rgb)
    y_pred['index'] = pd.to_datetime(y_pred['index'])

    tickvals, ticktext = traduzir_eixo_x(total_de_casos_amazonas['date'].tail(30), 6, 7)
    tickvals_pred, ticktext_pred = traduzir_eixo_x(y_pred['index'], 4, 7)
    
    tickvals.extend(tickvals_pred)
    ticktext.extend(ticktext_pred)
    
    ticktext = [x[:-4] for x in ticktext]
    
    fig.update_xaxes(tickformat= '%y/%m/%d', 
                     tickvals=tickvals, 
                     ticktext=ticktext)

    return fig

def show_rankings():
    df = updating_df()
    total_por_estado = updating_total_por_estado()
    ranking_nacional, ranking_municipal = updating_rankings(df, total_por_estado)

    return ranking_nacional, ranking_municipal