import streamlit as st
from controller import controller_vendas
from controller import controle_vendas_comparativo
from controller import Vendas_ano
from controller import Vendas_mês,ped_item
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import locale
from repositorio import get_oracle
import plotly.express as px
import pandas as pd
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def cards_vendas():

    st.sidebar.image("foto.png",use_column_width=True)

    st.write("""
        <style>
            body {
                background-image: url('foto.jpg'); /* Caminho relativo da imagem */
                background-size: cover; /* Ajusta o tamanho da imagem para cobrir todo o espaço */
                background-repeat: no-repeat; /* Evita a repetição da imagem */
                background-position: top center; /* Posiciona a imagem no topo e centraliza horizontalmente */
                color: white; /* Define a cor do texto como branco */
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Título da Página
    st.write("""
        <style>
            .nunito-header {
                font-family: 'Open-Sans', sans-serif;
                font-size: 48px; /* Tamanho da fonte */
                text-align: center; /* Centralizar o texto */
                font-weight: bold; /* Adicionando negrito */
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='nunito-header'>Flash de Vendas</div>", unsafe_allow_html=True)
    

    # Filtrar por período de análise
    data_inicio = st.sidebar.date_input("Selecione a data de início")
    data_fim = st.sidebar.date_input("Selecione a data de fim")

    if data_fim < data_inicio:
        st.warning("A data de fim não pode ser menor que a data de início. Por favor, selecione uma data de fim posterior à data de início.",icon="⚠️")
        st.stop()

    periodo_selecionadas = ["Ano", "Mês"]
    periodo = st.sidebar.selectbox("Selecione o período:", periodo_selecionadas)

    if periodo == "Ano":
        # Definir data llllfinal como a data atual menos um dia
        data_fimp = data_fim - relativedelta(years=1)
        # Definir data inicial como um ano antes da data final
        data_iniciop = data_inicio - relativedelta(years=1)
    if periodo == "Mês":
        # Definir data final como a data atual menos um dia
        data_fimp = data_fim - relativedelta(months=1)
        # Definir data inicial como um mês antes da data final
        data_iniciop = data_inicio - relativedelta(months=1)
    
    # Obter os dados filtrados do Oracle
    df_filtrado_oracle = get_oracle(data_inicio, data_fim)

    # Filtrar as modalidades únicas disponíveis
    modalidades_disponiveis = df_filtrado_oracle['modalidade'].unique()

    # Adicionar uma opção "Todas"
    modalidades_disponiveis = ["Todas"] + modalidades_disponiveis.tolist()

    # Criar o seletor na barra lateral para as modalidades
    flt_mod = st.sidebar.selectbox("Selecione a Plataforma", modalidades_disponiveis)

    # Aplicar o filtro de modalidade
    if flt_mod != "Todas":
        df_filtrado_oracle = df_filtrado_oracle[df_filtrado_oracle['modalidade'] == flt_mod]

    # Filtrar as lojas únicas disponíveis baseadas no resultado filtrado das modalidades
    lojas_disponiveis = df_filtrado_oracle['loja'].unique()

    # Adicionar uma opção "Todas"
    lojas_disponiveis = ["Todas"] + lojas_disponiveis.tolist()

    # Criar o seletor na barra lateral para as lojas
    status_lj = st.sidebar.selectbox("Selecione a Loja:", lojas_disponiveis)

    # Aplicar o filtro de loja
    if status_lj != "Todas":
        df_filtrado_oracle = df_filtrado_oracle[df_filtrado_oracle['loja'] == status_lj]

    # Filtrar as categorias únicas disponíveis baseadas no resultado filtrado das modalidades e lojas
    categorias_disponiveis = df_filtrado_oracle['categoriaN1'].unique()

    # Adicionar uma opção "Todas"
    categorias_disponiveis = ["Todas"] + categorias_disponiveis.tolist()

    # Criar o seletor na barra lateral para as categorias
    status_cat = st.sidebar.selectbox("Selecione a categoria:", categorias_disponiveis)

    # Aplicar o filtro de categoria
    if status_cat != "Todas":
        df_filtrado_oracle = df_filtrado_oracle[df_filtrado_oracle['categoriaN1'] == status_cat]
 
    controller = controller_vendas(data_inicio=data_inicio, data_fim=data_fim,flt_mod=flt_mod,status_lj=status_lj,status_cat=status_cat)
    controller1 = controle_vendas_comparativo(data_iniciop=data_iniciop,data_fimp=data_fimp,flt_mod=flt_mod,status_lj=status_lj,status_cat=status_cat)
    controller2 = Vendas_ano(data_inicio=data_inicio,data_fim=data_fim,periodo=periodo)
    controller3 = Vendas_mês(data_inicio=data_inicio,data_fim=data_fim,periodo=periodo)
    controller4 = ped_item(data_inicio=data_inicio,data_fim=data_fim)

    real_venda_total_formatadap = controller1['real_venda_total_formatadap'].replace('R$', '').replace('.', '').replace(',', '.')

    # Convertendo a string resultante em um número float
    real_venda_total_formatadap_float = float(real_venda_total_formatadap)

    percent_comparacao =  ((float(controller["vend_total_atual"])/float(controller1["vend_total_periodo"]))-1) * 100
    delta_str = f'{percent_comparacao:.2f}%'

    # Definindo o estilo CSS para os cards editáveis
    with open('card_css.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Títulos dos Cards
    st.write("<h3 style='text-align:center;'>Indicadores Globais</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric(label = "Meta Total de Venda",value = str(controller['meta_venda_total_formatada']))
    col2.metric(label = "Meta Total de Lucratividade",value = str(controller['meta_lucratividade_total_formatada']))
    col3.metric(label = "Meta Prevista de Lucro (%)",value = str(controller["meta_margem_lucro_percent"]))

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Realizado Total de Venda - Ano Passado", value=controller2['Venda_ano_passado'])
    col2.metric(label="Realizado Total de Lucratividade - Ano Passado", value='-')
    col3.metric(label="Margem Real de Lucro (%) - Ano Passado", value='-')

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Realizado Total de Venda - Mês Passado", value=controller3['Venda_mês_passado'])
    col2.metric(label="Realizado Total de Lucratividade - Mês Passado", value='-')
    col3.metric(label="Margem Real de Lucro (%) - Mês Passado", value='-')

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Realizado Total de Venda", value=str(controller['Realizado Total de Venda']))
    col2.metric(label="Realizado Total de Lucratividade", value='-')
    col3.metric(label="Margem Real de Lucro (%)", value='-')

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Performace percenttual de Venda", value=str(controller['teste']))
    col2.metric(label="Performace percenttual de Lucratividade", value='-')
    col3.metric(label="Diferença de Margem Real de Lucro (%)", value='-')

    st.divider()

    st.write("<h3 style='text-align:center;'>Descrição de Compras</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric(label="Quantidade de Pedidos", value=str(controller4['Pedido']))
    col2.metric(label="Média de Itens", value=str(controller4['Itens']))
    col3.metric(label="Ticket Medio", value=str(controller4['tkt']))

    st.divider()

    st.write("<h3 style='text-align:center;'>Performace por Plataforma</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5  = st.columns(5)
    col1.metric(label="REPRESENTATIVIDADE", value=str(controller['Repre_plat']))
    col2.metric(label="TOTAL", value=str(controller['Total_plat']),delta=str(controller1['total_plat']))
    col3.metric(label="TOTAL SITE MERCADO", value=str(controller['SM']),delta=str(controller1['SMp']))
    col4.metric(label="TOTAL IFOOD", value=str(controller['Ifood']),delta=str(controller1['Ifoodp']))
    col5.metric(label="TOTAL VIPCOMMERCE", value=str(controller['VIP']),delta=str(controller1['VPp']))

    st.divider()

    st.write("<h3 style='text-align:center;'>Performace por Modalidade</h3>", unsafe_allow_html=True)
    
    col1, col2, col3,col4= st.columns(4)
    col1.metric(label="RETIRA SM", value=str(controller['Ret_SM']),delta=str(controller1['ret_smp']))
    col2.metric(label="RETIRA IFOOD", value=str(controller['Ret_Ifood']),delta=str(controller1['ret_ifoodp']))
    col3.metric(label="RETIRA VIPCOMMERCE", value=str(controller['Ret_VP']),delta=str(controller1['ret_Vpp']))
    col4.metric(label="TOTAL RETIRA", value=str(controller['Total_smifd_r']),delta=str(controller1['total_retp']))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="ENTREGA SM", value=str(controller['Ent_SM']),delta=str(controller1['ent_SM']))
    col2.metric(label="ENTREGA IFOOD", value=str(controller['Ent_Ifood']),delta=str(controller1['ent_ifoodp']))
    col3.metric(label="ENTREGA VIPCOMMERCE", value=str(controller['Ent_VP']),delta=str(controller1['ent_Vpp']))
    col4.metric(label="TOTAL ENTREGA", value=str(controller['Total_smifd_e']),delta=str(controller1['total_entp']))
   
    st.write("<h3 style='text-align:center;'>Rankings</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Exibir as tabelas dentro das colunas
    with col1:
        st.write("<h3 style='text-align:center;'>Top 10 Produtos</h3>", unsafe_allow_html=True)
        st.table(controller['Top_prod'].style.set_properties(**{'border-bottom': '1px solid rgba(2, 2, 2, 0.1)', 'border-right': '1px solid rgba(2, 2, 2, 0.1)', 'vertical-align': 'middle', 'padding': '0.25rem 0.375rem', 'font-weight': '400', 'font-size': '12px'}))

    with col2:
        st.write("<h3 style='text-align:center;'>Top 10 Categorias</h3>", unsafe_allow_html=True)
        st.table(controller['Top_cat'].style.set_properties(**{'border-bottom': '1px solid rgba(2, 2, 2, 0.1)', 'border-right': '1px solid rgba(2, 2, 2, 0.1)', 'vertical-align': 'middle', 'padding': '0.25rem 0.375rem', 'font-weight': '400', 'font-size': '12px'}))
    with col3:
        st.write("<h3 style='text-align:center;'>Top 10 Lojas</h3>", unsafe_allow_html=True)
        st.table(controller['Top_loja'].style.set_properties(**{'border-bottom': '1px solid rgba(2, 2, 2, 0.1)', 'border-right': '1px solid rgba(2, 2, 2, 0.1)', 'vertical-align': 'middle', 'padding': '0.25rem 0.375rem', 'font-weight': '400', 'font-size': '12px'}))
 
    st.write("<h3 style='text-align:center;'>Desdobramento por Categoria</h3>", unsafe_allow_html=True)

    df_produtoSF_grafico = controller['grafico']

    fig1 = px.bar(df_produtoSF_grafico, x='categoriaN1', y='valor_pedido', barmode='group',text='valor_pedido')
    fig1.update_traces(marker_color='#062952')
    fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig1.update_layout(title='Performace por Categoria',
                       uniformtext_minsize=8, 
                       uniformtext_mode='hide',
                       xaxis=dict(showgrid=False),
                       yaxis=dict(showgrid=False),
                       xaxis_title='',
                       yaxis_title='Valor do Pedido',
                       yaxis_tickformat='R$,.2f')
    fig1.update_layout(width=900,height=500)
    st.plotly_chart(fig1)

    # st.table(controller["tabela"])
    st.table(controller["tabela"].style.set_table_styles([{
    'selector': 'thead th', 
    'props': [
        ('background-color', '#062952'), 
        ('color', 'white')  # Cor do texto
    ]
}]))

    # Criando o primeiro gráfico de barras

    # st.write("<h3 style='text-align:center;'>Desdobramento por Produto</h3>", unsafe_allow_html=True)

    # st.dataframe(controller['teste1'].tail(100), width=1200, height=1000)
  
    return data_inicio, data_fim
