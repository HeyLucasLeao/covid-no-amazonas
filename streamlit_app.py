import streamlit as st
from src.data import ranking_nacional, ranking_municipal
from src.plot import *
from src.model import smape

opcoes = (
    'Home',
    "Dados Diários",
    "Dados por Mapa Coroplético",
    "Gráfico de Dispersão", 
    "Frequência Mensal",
    "Ranking por 100K Óbitos",
    "Quadro Evolutivo",
    "Crescimento nos Últimos Dias",
    "Predição de Tendência",
    "Ocupação em Hospitais",
    "Média de Dados por Dia da Semana"
)

box = st.sidebar.selectbox("Selecione a página", opcoes)

if box == 'Home':
    st.header("Dados sobre Covid-19 com foco no Amazonas")
    st.write("""Projeto pessoal para fins educativos com finalidade de uma análise extensa, crítica e exploratória dos dados de Covid-19 dentro do estado do Amazonas.
    Para isso, utilizo um [banco de dados](https://github.com/wcota/covid19br) junto a informações da Secretaria de Estado de Saúde do Amazonas.""")
    st.write("[Notícias da Fundação de Vigilância em Saúde do Amazonas (FVS-AM)](https://github.com/HeyLucasLeao/noticias-FVS-AM)")
    st.write("[Covid19map](https://www.covid19map.com.br/case-map)")
    st.write("[Fonte deste repositório](https://github.com/HeyLucasLeao/covid-no-amazonas)")
    st.write("[Contato](https://t.me/heylucasleao)")
    st.write("[LinkedIn](https://www.linkedin.com/in/lucas-le%C3%A3o-698a49206/)""")
elif box == "Ranking por 100K Óbitos":
    st.write("### Nacional")
    st.write(ranking_nacional)
    st.write("### Municipal")
    st.write(ranking_municipal)
elif box == "Dados por Mapa Coroplético":
    st.write("### Nacional")
    st.plotly_chart(show_mapa_nacional())
    st.write("### Municipal")
    st.plotly_chart(show_mapa_municipal())
elif box == "Gráfico de Dispersão":
    st.plotly_chart(show_grafico_de_dispersao())
elif box == "Frequência Mensal":
    st.plotly_chart(show_dados_mensais())
elif box == "Quadro Evolutivo":
    st.plotly_chart(show_quadro_evolutivo())
elif box == "Dados Diários":
    st.write("### Casos & Óbitos no Amazonas")
    st.plotly_chart(show_dados_diarios_casos_e_obitos())
    st.plotly_chart(show_dados_diarios_obitos())
elif box == "Predição de Tendência":
    st.write("### Predição de Tendência de Casos")
    st.plotly_chart(show_predicao())
    st.write(f'###### Média de Erro Percentual: {smape} %')
elif box == "Crescimento nos Últimos Dias":
    st.plotly_chart(show_crescimento_dos_ultimos_14_dias())
elif box == "Ocupação em Hospitais":
    st.plotly_chart(show_ocupacao_em_hospitais())
elif box == "Média de Dados por Dia da Semana":
    st.plotly_chart(show_dia_da_semana())