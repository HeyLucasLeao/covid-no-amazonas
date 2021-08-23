import streamlit as st
from src.plot import *

opcoes = (
    'Home',
    "Dados Diários",
    "Dados por Mapa Coroplético",
    "Gráfico de Dispersão", 
    "Frequência Mensal",
    "Ranking por 100K Óbitos",
    "Quadro Evolutivo",
    "Crescimento Semanal",
    "Predição de Tendência",
    "Ocupação em Hospitais",
    "Média de Dados por Dia da Semana"
)

box = st.sidebar.selectbox("Selecione a página", opcoes)
st.sidebar.info("[Notícias da Fundação de Vigilância em Saúde do Amazonas (FVS-AM)](https://share.streamlit.io/heylucasleao/noticias-fvs-am/main)")
st.sidebar.info("[Covid19map](https://www.covid19map.com.br/)")

if box == 'Home':
    st.header("Dados sobre Covid-19 com foco no Amazonas")
    st.write("""Projeto pessoal para fins educativos com finalidade de uma análise extensa, crítica e exploratória dos dados de Covid-19 dentro do estado do Amazonas.
    Para isso, utilizo um [banco de dados](https://github.com/wcota/covid19br) junto a informações da Secretaria de Estado de Saúde do Amazonas.
    
    Selecione a página no canto superior esquerdo da tela.""")
    st.write("[Repositório deste projeto](https://github.com/HeyLucasLeao/covid-no-amazonas)")
    st.write("[Contato](https://t.me/heylucasleao)")
    st.write("[LinkedIn](https://www.linkedin.com/in/lucas-le%C3%A3o-698a49206/)""")
elif box == "Ranking por 100K Óbitos":
    ranking_nacional, ranking_municipal = show_rankings()
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
    st.write("### Dados de Casos & Óbitos no Amazonas")
    st.plotly_chart(show_dados_diarios_casos_e_obitos())
    st.write("### Dados de Óbitos no Amazonas")
    st.plotly_chart(show_dados_diarios_obitos())
#elif box == "Predição de Tendência":
#    st.write("### Predição de Tendência de Casos")
#    st.plotly_chart(show_predicao())
#    with open(r'src/pred/smape.txt', 'r') as file:
#        smape = file.read()
#    st.write(f'###### Média de Erro Percentual: {smape} %')
elif box == "Crescimento Semanal":
    st.plotly_chart(show_crescimento())
elif box == "Ocupação em Hospitais":
    st.plotly_chart(show_ocupacao_em_hospitais())
elif box == "Média de Dados por Dia da Semana":
    st.plotly_chart(show_dia_da_semana())
