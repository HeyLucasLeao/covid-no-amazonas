import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px


from src.data import *
from src.functions_to_date import *
from src.model import y_pred

import warnings
warnings.filterwarnings("ignore")
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
rgb = 'rgb(34, 34, 34)'
red = '#812929'
GLOBAL_TEMPLATE = 'plotly_dark'
MAPBOX_TOKEN = 'pk.eyJ1IjoiaGV5bHVjYXNsZWFvIiwiYSI6ImNrcDRqeW1yNzAzaHIycHNiZWo1bHBqeGkifQ.kw4Buc12S2g1CTZ7KhXwYA'

def show_grafico_de_dispersao():
    fig = make_subplots(subplot_titles=('10 Cidades com os Maiores Casos & Óbitos Registrados por COVID-19', 
                                        'Relação de Casos & Óbitos por 100k Habitantes por Estado'),
                        rows=1, cols=2)

    ### Configuração de gráfico a esquerda
    fig.add_trace(go.Scatter(x = total_10_maiores_cidades['city'], 
                             y= total_10_maiores_cidades['totalCases'],
                             mode='markers',
                     marker=dict(color = total_10_maiores_cidades['totalCases'],
                                colorscale= ['cyan', 'crimson'],
                                size=total_10_maiores_cidades['totalCases'],
                                sizemode='area',
                                sizeref=110,
                                showscale=False),
                             text=total_10_maiores_cidades['deaths'],
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
    fig = px.bar(data_frame=total_de_casos_amazonas, 
                 x='date', 
                 y='newCases', 
                 hover_data={"newCases": ":,2f", 'newDeaths': ":,2f",'date': False}, 
                 labels={"newCases": "Novos Casos", "date": 'Data', 'newDeaths': 'Novos Óbitos'},
                 color = 'newCases', 
                 opacity= 0.75)

    fig.add_trace(go.Scatter(x=total_de_casos_amazonas['date'],
                             y=tendencia_de_novos_casos.round(), 
                             line=dict(color=red, width=1), 
                             name="Holt-Winters (SEHW) - Casos",
                             mode='lines', 
                             hoverinfo="y", 
                             showlegend=False, 
                             hovertemplate="%{y}"))


    fig.add_trace(go.Scatter(x=total_de_casos_amazonas['date'], 
                             y=tendencia_de_novas_mortes, 
                             line=dict(color=red, width=1), 
                             name="Holt-Winters (SEHW) - Óbitos",
                             mode='lines',
                             hoverinfo='y' , 
                             showlegend=False, 
                             hovertemplate="%{y}"))

    fig.add_trace(go.Scatter(x=tabela_de_epocas_festivas_com_dados['date'], 
                             y=tabela_de_epocas_festivas_com_dados['newCases'], 
                             line=dict(color='steelblue', width=0.01),  
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
    fig = px.bar(data_frame = total_de_casos_amazonas, x='date', y='newDeaths', color='newDeaths', labels={'newDeaths': 'Óbitos', 'date': 'Data'})

    fig.update_traces(hovertemplate="%{y}", name='Óbitos')
    fig.add_trace(go.Scatter(x=total_de_casos_amazonas['date'], 
                             y=tendencia_de_novas_mortes, 
                             line=dict(color=red, width=1), 
                             name="Holt-Winters (SEHW) - Óbitos",
                             mode='lines',
                             hoverinfo='y' , 
                             showlegend=False, 
                             hovertemplate="%{y}",
                             line_shape= 'spline'))

    fig.add_trace(go.Scatter(x=tabela_de_epocas_festivas_com_dados['date'], 
                             y=tabela_de_epocas_festivas_com_dados['newDeaths'], 
                             line=dict(color='steelblue', width=0.01),  
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



def show_crescimento_dos_ultimos_14_dias():    
    ###Criação de Gráfico
    fig = px.bar(crescimento.tail(14).round(2), 
                  y='valor',
                  x='date', 
                  color = 'valor',
                  labels = {'valor': 'Percentual (%)', 'date': 'Data', 'percentual': "Percentual (%)"},
                color_continuous_scale=['mediumaquamarine', 'maroon'],
                width=800, height=800,facet_col='variavel')


    fig.update_traces(hovertemplate="%{y} %")
    fig.update_layout(hovermode='x', 
                      separators=",.",
                      template=GLOBAL_TEMPLATE,
                      paper_bgcolor=rgb,
                     plot_bgcolor=rgb)

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))

    fig.add_hline(y=0)
    
    
    tickvals, ticktext = traduzir_eixo_x(crescimento['date'].tail(14), 0, 4)
    
    ticktext = [x[:-4] for x in ticktext]
    
    fig.update_xaxes(tickformat= '%y/%m/%d', 
                     tickvals=tickvals, 
                     ticktext=ticktext)
    fig.update_yaxes(matches=None)
    return fig

def show_dia_da_semana():
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
    fig = go.Figure()
    
    
    fig.add_trace(go.Bar(
                 x=total_de_casos_amazonas['date'].tail(30), 
                 y=total_de_casos_amazonas['newCases'].tail(30),
                hoverinfo='skip'))

    fig.update_traces(marker_color='gray')

    fig.add_trace(go.Scatter(x=total_de_casos_amazonas['date'].tail(30),
                             y=tendencia_de_novos_casos.round().tail(30), 
                             line=dict(color=red, width=1), 
                             name="Holt-Winters (SEHW) - Casos",
                             mode='lines', 
                             hoverinfo="y", 
                             showlegend=False, 
                             hovertemplate="%{y}",
                             fillcolor='Gray'))

    fig.add_trace(go.Scatter(x=y_pred.index, 
                             y=y_pred.values, 
                             line=dict(color=red, width=1), 
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
    
    tickvals, ticktext = traduzir_eixo_x(total_de_casos_amazonas['date'].tail(30), 6, 7)
    tickvals_pred, ticktext_pred = traduzir_eixo_x(y_pred.index, 4, 7)
    
    tickvals.extend(tickvals_pred)
    ticktext.extend(ticktext_pred)
    
    ticktext = [x[:-4] for x in ticktext]
    
    fig.update_xaxes(tickformat= '%y/%m/%d', 
                     tickvals=tickvals, 
                     ticktext=ticktext)

    return fig