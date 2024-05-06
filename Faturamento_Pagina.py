import streamlit as st
from controller import controller_faturamento
from controller import controller_faturamento1
from dateutil.relativedelta import relativedelta
from repositorio import get_oracle
import pandas as pd
import locale
from babel import Locale
from babel.numbers import format_currency
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import datetime
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def faturamento():
    data_inicio = st.sidebar.date_input("Selecione a data de início")
    data_fim = st.sidebar.date_input("Selecione a data de fim")

    periodo_selecionadas = ["Ano", "Mês"]
    periodo = st.sidebar.selectbox("Selecione o período:", periodo_selecionadas)

    if periodo == "Ano":
        data_fimp = data_fim - relativedelta(years=1)
        data_iniciop = data_inicio - relativedelta(years=1)
    if periodo == "Mês":
        data_fimp = data_fim - relativedelta(months=1)
        data_iniciop = data_inicio - relativedelta(months=1)

    with open('card_css.css') as f:
      st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    if data_inicio and data_fim:
      controller= controller_faturamento(data_inicio=data_inicio, data_fim=data_fim)
      controller1 = controller_faturamento1(data_iniciop=data_iniciop,data_fimp=data_fimp)

    df_smplataforma = pd.merge(controller['SM'], controller1['SM'], left_index=True, right_index=True)
    df_smplataforma.fillna(0,inplace=True)
    df_smplataforma['ENTREGA_x_x'] = df_smplataforma['ENTREGA_x_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    df_smplataforma['ENTREGA_x_y'] = df_smplataforma['ENTREGA_x_y'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    df_smplataforma['Var.R$_Entrega'] = df_smplataforma['ENTREGA_x_x'] / df_smplataforma['ENTREGA_x_y']*100
    df_smplataforma['Var.R$_Entrega'] = df_smplataforma['Var.R$_Entrega'].map('{:.2f}%'.format)

    df_smplataforma['RETIRA_x_x'] = df_smplataforma['RETIRA_x_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    df_smplataforma['RETIRA_x_y'] = df_smplataforma['RETIRA_x_y'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    df_smplataforma['Var.R$_Retira'] = df_smplataforma['RETIRA_x_x'] / df_smplataforma['RETIRA_x_y']*100
    df_smplataforma['Var.R$_Retira'] = df_smplataforma['Var.R$_Retira'].map('{:.2f}%'.format)

    df_smplataforma['Var.qtd_Entrega'] = df_smplataforma['ENTREGA_y_x'] / df_smplataforma['ENTREGA_y_y']*100
    df_smplataforma['Var.qtd_Entrega'] = df_smplataforma['Var.qtd_Entrega'].map('{:.2f}%'.format)

    df_smplataforma['Var.qtd_Retira'] = df_smplataforma['RETIRA_y_x'] / df_smplataforma['RETIRA_y_y']*100
    df_smplataforma['Var.qtd_Retira'] = df_smplataforma['Var.qtd_Retira'].map('{:.2f}%'.format)

    df_smplataforma['Tkt.Ent 📍'] = df_smplataforma['ENTREGA_x_x'] / df_smplataforma['ENTREGA_y_x']
    df_smplataforma['Tkt.Ret 📍'] = df_smplataforma['RETIRA_x_x'] / df_smplataforma['RETIRA_y_x']

    df_smplataforma['Tkt.Ent 📅'] = df_smplataforma['ENTREGA_x_y'] / df_smplataforma['ENTREGA_y_y']

    df_smplataforma['Tkt.Ret 📅'] = df_smplataforma['RETIRA_x_y'] / df_smplataforma['RETIRA_y_y']

    df_smplataforma['Δ Tkt.Ent'] = df_smplataforma['Tkt.Ent 📅'] / df_smplataforma['Tkt.Ent 📍']*100
    df_smplataforma['Δ Tkt.Ent'] = df_smplataforma['Δ Tkt.Ent'].map('{:.2f}%'.format)
    df_smplataforma['Δ Tkt.Ret'] = df_smplataforma['Tkt.Ret 📅'] / df_smplataforma['Tkt.Ret 📍']*100
    df_smplataforma['Δ Tkt.Ret'] = df_smplataforma['Δ Tkt.Ret'].map('{:.2f}%'.format)

    df_smplataforma['Δ Pedido.Ent'] = df_smplataforma['ENTREGA_y_x'] / df_smplataforma['ENTREGA_y_y']*100
    df_smplataforma['Δ Pedido.Ent'] = df_smplataforma['Δ Pedido.Ent'].map('{:.2f}%'.format)
    df_smplataforma['Δ Pedido.Ret'] = df_smplataforma['RETIRA_y_x'] / df_smplataforma['RETIRA_y_y']*100
    df_smplataforma['Δ Pedido.Ret'] = df_smplataforma['Δ Pedido.Ret'].map('{:.2f}%'.format)

    df_smplataforma['Tkt.Ent 📅'] = df_smplataforma['Tkt.Ent 📅'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_smplataforma['Tkt.Ret 📅'] = df_smplataforma['Tkt.Ret 📅'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_smplataforma['Tkt.Ret 📍'] = df_smplataforma['Tkt.Ret 📍'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_smplataforma['Tkt.Ent 📍'] = df_smplataforma['Tkt.Ent 📍'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_smplataforma['ENTREGA_x_x'] = df_smplataforma['ENTREGA_x_x'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_smplataforma['RETIRA_x_x'] = df_smplataforma['RETIRA_x_x'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_smplataforma['ENTREGA_x_y'] = df_smplataforma['ENTREGA_x_y'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_smplataforma['RETIRA_x_y'] = df_smplataforma['RETIRA_x_y'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))

    df_smplataforma.rename(columns={'ENTREGA_x_x': 'R$ ENT 📍'}, inplace=True)
    df_smplataforma.rename(columns={'RETIRA_x_x': 'R$ RET 📍'}, inplace=True)
    df_smplataforma.rename(columns={'ENTREGA_y_x': 'ENTREGA PEDIDO 📍'}, inplace=True)
    df_smplataforma.rename(columns={'RETIRA_y_x': 'RETIRA PEDIDO 📍'}, inplace=True)
    df_smplataforma.rename(columns={'Var.R$_Entrega': 'Δ ENTREGA'}, inplace=True)
    df_smplataforma.rename(columns={'ENTREGA_x_y': 'R$ ENT 📅'}, inplace=True)
    df_smplataforma.rename(columns={'RETIRA_x_y': 'R$ RET 📅'}, inplace=True)
    df_smplataforma.rename(columns={'ENTREGA_y_y': 'ENTREGA PEDIDO 📅'}, inplace=True)
    df_smplataforma.rename(columns={'RETIRA_y_y': 'RETIRA PEDIDO 📅'}, inplace=True)
    df_smplataforma.rename(columns={'Var.R$_Retira': 'Δ RETIRA'}, inplace=True)

    nova_ordem_colunas = ['R$ ENT 📅','R$ ENT 📍','Δ ENTREGA','R$ RET 📅','R$ RET 📍',
                          'Δ RETIRA','ENTREGA PEDIDO 📅','ENTREGA PEDIDO 📍','Δ Pedido.Ent','RETIRA PEDIDO 📅',
                          'RETIRA PEDIDO 📍','Δ Pedido.Ret','Tkt.Ent 📅','Tkt.Ent 📍','Δ Tkt.Ent',
                          'Tkt.Ret 📅','Tkt.Ret 📍','Δ Tkt.Ret']

    df_smplataforma = df_smplataforma[nova_ordem_colunas]
    df_smplataforma1000 = df_smplataforma
    df_smplataforma1000['Δ ENTREGA'] = df_smplataforma1000['Δ ENTREGA'].str.replace('%', '').astype(float)
    df_smplataforma1000['Δ ENTREGA'] = df_smplataforma1000['Δ ENTREGA'].round(2)

    df_smplataforma1001 = df_smplataforma
    df_smplataforma1001['Δ RETIRA'] = df_smplataforma1001['Δ RETIRA'].str.replace('%', '').astype(float)
    df_smplataforma1001['Δ RETIRA'] = df_smplataforma1001['Δ RETIRA'].round(2)

    df_smplataforma1000['Δ Pedido.Ent'] = df_smplataforma1000['Δ Pedido.Ent'].str.replace('%', '').astype(float)
    df_smplataforma1000['Δ Pedido.Ent'] = df_smplataforma1000['Δ Pedido.Ent'].round(2)

    df_smplataforma1000['Δ Pedido.Ret'] = df_smplataforma1000['Δ Pedido.Ret'].str.replace('%', '').astype(float)
    df_smplataforma1000['Δ Pedido.Ret'] = df_smplataforma1000['Δ Pedido.Ret'].round(2)

    df_smplataforma1000['Δ Tkt.Ent'] = df_smplataforma1000['Δ Tkt.Ent'].str.replace('%', '').astype(float)
    df_smplataforma1000['Δ Tkt.Ent'] = df_smplataforma1000['Δ Tkt.Ent'].round(2)

    df_smplataforma1000['Δ Tkt.Ret'] = df_smplataforma1000['Δ Tkt.Ret'].str.replace('%', '').astype(float)
    df_smplataforma1000['Δ Tkt.Ret'] = df_smplataforma1000['Δ Tkt.Ret'].round(2)

    st.write("<h3 style='text-align:center;'>Grafico de Faturamento E-commerce</h3>", unsafe_allow_html=True)

    df_produtoSF_grafico = controller['grafico10']

    fig1 = px.bar(df_produtoSF_grafico, x='Periodo', y='Valor', barmode='group',text='Valor')
    fig1.update_traces(marker_color='#062952')
    fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig1.update_layout(uniformtext_minsize=8, 
                       uniformtext_mode='hide',
                       xaxis=dict(showgrid=False),
                       yaxis=dict(showgrid=False),
                       xaxis_title='',
                       yaxis_title='Faturamento')
    fig1.update_layout(width=900,height=500)
    st.plotly_chart(fig1)

    data_atual = datetime.datetime.now()
    mes_atual = data_atual.month
    ano_atual = data_atual.year

 
    # st.write(f'Crescimento Percentual: {crescimento_percentual:.2f}%')
#####################################333
    st.divider()

    st.write("<h3 style='text-align:center;'>Grafico Comparativo YoY</h3>", unsafe_allow_html=True)

    df_produtoSF_grafico = controller['grafico11']
    
    fig2 = px.bar(df_produtoSF_grafico, x='Valor', y='Periodo', barmode='group',text='Valor', orientation='h')
    fig2.update_traces(marker_color='#062952')
    fig2.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig2.update_layout(uniformtext_minsize=8, 
                       uniformtext_mode='hide',
                       xaxis=dict(showgrid=False),
                       yaxis=dict(showgrid=False),
                       xaxis_title='',
                       yaxis_title='Faturamento')
    fig2.update_layout(width=900,height=500)
    st.plotly_chart(fig2)

    st.write('Desempenho percentual YoY : ')

    st.divider()

    ######################################

    st.write("<h3 style='text-align:center;'>Grafico Comparativo Real x Meta</h3>", unsafe_allow_html=True)

    df_produtoSF_grafico = controller['grafico12']

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=df_produtoSF_grafico['Periodo'], y=df_produtoSF_grafico['Meta_Venda'], name='Meta Venda', text=df_produtoSF_grafico['Meta_Venda'].apply(lambda x: locale.currency(x, grouping=True)), marker_color='#888888', width=0.3))
    fig3.add_trace(go.Bar(x=df_produtoSF_grafico['Periodo'], y=df_produtoSF_grafico['Valor'], name='Valor', text=df_produtoSF_grafico['Valor'].apply(lambda x: locale.currency(x, grouping=True)), marker_color='#062952', width=0.3 ))


    fig3.update_traces(textposition='outside')
    fig3.update_layout(
                    xaxis_title='',
                    yaxis_title='Faturamento',
                    width=900, height=500,
                    uniformtext_minsize=8,
                    uniformtext_mode='hide',
                    yaxis=dict(showgrid=False),
                    xaxis=dict(
                        showgrid=False,
                        tickmode='array',
                        tickvals=[]
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=0,
                        xanchor="center",
                        x=0.5
                    ),
                    barmode='group')
    st.plotly_chart(fig3)

       # Calcular o mesmo mês e ano do ano passado
    mes_passado = mes_atual
    ano_passado = ano_atual - 1

    # crescimento_percentual = ((valor_mes_ano_atual - valor_mes_ano_passado) / valor_mes_ano_passado) * 100

    st.write(f'Crescimento Anual: {mes_atual}/{ano_atual} Vs {mes_passado}/{ano_passado} :  📊')

    st.divider()

##########################################

    st.write("<h3 style='text-align:center;'>Faturamento Total</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric(label = "Faturamento Total",value = controller['TOTAL_FATSF'])
    col2.metric(label = "Pedidos Totais",value = controller['TOTAL_PEDIDO'])
    col3.metric(label = "Tkt.Médio Total",value = controller['TOTAL_TKT'])

    st.divider()

    total10 = pd.merge(controller['Total'], controller1['Total'], left_index=True, right_index=True)

    total10.drop(columns=['IFOOD_x_x'], inplace=True)
    total10.drop(columns=['SM_x_x'], inplace=True)
    total10.drop(columns=['IFOOD_y_x'], inplace=True)
    total10.drop(columns=['SM_y_x'], inplace=True)
    total10.drop(columns=['IFOOD_x_y'], inplace=True)
    total10.drop(columns=['SM_x_y'], inplace=True)
    total10.drop(columns=['IFOOD_y_y'], inplace=True)
    total10.drop(columns=['SM_y_y'], inplace=True)

    total10['Total_x_y'] = total10['Total_x_y'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)

    total10['TKt 📅'] = total10['Total_x_y']/total10['Total_y_y']
    total10['TKt 📅'] = total10['TKt 📅'].round(2)

    total10['Total_x_x'] = total10['Total_x_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    total10['TKt 📍'] = total10['Total_x_x']/total10['Total_y_x']
    total10['TKt 📍'] = total10['TKt 📍'].round(2)

    total10['Δ TKT'] = ((total10['TKt 📍']/total10['TKt 📅'])-1)*100
    total10['Δ TKT'] = total10['Δ TKT'].round(2)

    total10['Δ Venda'] = ((total10['Total_x_x']/total10['Total_x_y'])-1)*100
    total10['Δ Venda'] = total10['Δ Venda'].round(2)

    total10['Δ Absoluta'] = total10['Total_x_x'] - total10['Total_x_y']
    total10['Δ Absoluta'] = total10['Δ Absoluta'].round(2)

    total10['Δ Pedido'] = ((total10['Total_y_x']/total10['Total_y_y'])-1)*100
    total10['Δ Pedido'] = total10['Δ Pedido'].round(2)

    total10 = total10.sort_values(by='Δ Absoluta', ascending=False)

    total10['Total_x_x'] = total10['Total_x_x'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    total10['Δ Absoluta'] = total10['Δ Absoluta'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    total10['Total_x_y'] = total10['Total_x_y'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    total10['TKt 📅'] = total10['TKt 📅'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    total10['TKt 📍'] = total10['TKt 📍'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    total10['Δ Pedido'] = total10['Δ Pedido'].map('{:.2f}%'.format)
    total10['Δ Venda'] = total10['Δ Venda'].map('{:.2f}%'.format)
    total10['Δ TKT'] = total10['Δ TKT'].map('{:.2f}%'.format)
   
    total10.rename(columns={'Total_x_y': 'Venda Total 📅'}, inplace=True)
    total10.rename(columns={'Total_x_x': 'Venda Total 📍'}, inplace=True)
    total10.rename(columns={'Total_y_y': 'Pedido Total 📅'}, inplace=True)
    total10.rename(columns={'Total_y_x': 'Pedido Total 📍'}, inplace=True)

    nova_ordem = ['Venda Total 📅','Venda Total 📍','Δ Absoluta','Δ Venda','Pedido Total 📅','Pedido Total 📍','Δ Pedido','TKt 📅','TKt 📍','Δ TKT']

    total10 = total10[nova_ordem]

    st.table(total10.style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', '#062952'), ('color', 'white'), ('text-align', 'center')]},
        {'selector': 'tbody td', 'props': [('text-align', 'center')]}
    ]))

    st.write("<h3 style='text-align:center;'>Faturamento Ifood</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)

    col1.metric(label = "Faturamento Total",value = controller['TOTAL_IFOOD'])
    col2.metric(label = "Pedidos Totais",value = controller['TOTAL_PEDIDOIFOOD'])
    col3.metric(label = "Tkt.Médio Total",value = controller['TOTAL_TKTIFOOD'])

    df_ifoodplataforma = pd.merge(controller['Ifood'], controller1['Ifood'], left_index=True, right_index=True)
    df_ifoodplataforma.fillna(0,inplace=True)
    df_ifoodplataforma['ENTREGA R$_x'] = df_ifoodplataforma['ENTREGA R$_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    df_ifoodplataforma['ENTREGA R$_y'] = df_ifoodplataforma['ENTREGA R$_y'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    df_ifoodplataforma['Var.R$_Entrega'] = df_ifoodplataforma['ENTREGA R$_x'] / df_ifoodplataforma['ENTREGA R$_y']*100
    df_ifoodplataforma['Var.R$_Entrega'] = df_ifoodplataforma['Var.R$_Entrega'].map('{:.2f}%'.format)

    df_ifoodplataforma['RETIRA R$_x'] = df_ifoodplataforma['RETIRA R$_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    df_ifoodplataforma['RETIRA R$_y'] = df_ifoodplataforma['RETIRA R$_y'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    df_ifoodplataforma['Var.R$_Retira'] = df_ifoodplataforma['RETIRA R$_x'] / df_ifoodplataforma['RETIRA R$_y']*100
    df_ifoodplataforma['Var.R$_Retira'] = df_ifoodplataforma['Var.R$_Retira'].map('{:.2f}%'.format)

    df_ifoodplataforma['Var.qtd_Entrega'] = df_ifoodplataforma['ENTREGA - PEDIDO_x'] / df_ifoodplataforma['ENTREGA - PEDIDO_y']*100
    df_ifoodplataforma['Var.qtd_Entrega'] = df_ifoodplataforma['Var.qtd_Entrega'].map('{:.2f}%'.format)

    df_ifoodplataforma['Var.qtd_Retira'] = df_ifoodplataforma['RETIRA - PEDIDO_x'] / df_ifoodplataforma['RETIRA - PEDIDO_y']*100
    df_ifoodplataforma['Var.qtd_Retira'] = df_ifoodplataforma['Var.qtd_Retira'].map('{:.2f}%'.format)

    df_ifoodplataforma['Tkt.Ent 📍'] = df_ifoodplataforma['ENTREGA R$_x'] / df_ifoodplataforma['ENTREGA - PEDIDO_x']
    df_ifoodplataforma['Tkt.Ret 📍'] = df_ifoodplataforma['RETIRA R$_x'] / df_ifoodplataforma['RETIRA - PEDIDO_x']

    df_ifoodplataforma['Tkt.Ent 📅'] = df_ifoodplataforma['ENTREGA R$_y'] / df_ifoodplataforma['ENTREGA - PEDIDO_y']

    df_ifoodplataforma['Tkt.Ret 📅'] = df_ifoodplataforma['RETIRA R$_y'] / df_ifoodplataforma['RETIRA - PEDIDO_y']

    df_ifoodplataforma['Δ Tkt.Ent'] = df_ifoodplataforma['Tkt.Ent 📅'] / df_ifoodplataforma['Tkt.Ent 📍']*100
    df_ifoodplataforma['Δ Tkt.Ent'] = df_ifoodplataforma['Δ Tkt.Ent'].map('{:.2f}%'.format)
    df_ifoodplataforma['Δ Tkt.Ret'] = df_ifoodplataforma['Tkt.Ret 📅'] / df_ifoodplataforma['Tkt.Ret 📍']*100
    df_ifoodplataforma['Δ Tkt.Ret'] = df_ifoodplataforma['Δ Tkt.Ret'].map('{:.2f}%'.format)

    df_ifoodplataforma['Δ Pedido.Ent'] = df_ifoodplataforma['ENTREGA - PEDIDO_x'] / df_ifoodplataforma['ENTREGA - PEDIDO_y']*100
    df_ifoodplataforma['Δ Pedido.Ent'] = df_ifoodplataforma['Δ Pedido.Ent'].map('{:.2f}%'.format)
    df_ifoodplataforma['Δ Pedido.Ret'] = df_ifoodplataforma['RETIRA - PEDIDO_x'] / df_ifoodplataforma['RETIRA - PEDIDO_y']*100
    df_ifoodplataforma['Δ Pedido.Ret'] = df_ifoodplataforma['Δ Pedido.Ret'].map('{:.2f}%'.format)

    df_ifoodplataforma['Tkt.Ent 📅'] = df_ifoodplataforma['Tkt.Ent 📅'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_ifoodplataforma['Tkt.Ret 📅'] = df_ifoodplataforma['Tkt.Ret 📅'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_ifoodplataforma['Tkt.Ret 📍'] = df_ifoodplataforma['Tkt.Ret 📍'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_ifoodplataforma['Tkt.Ent 📍'] = df_ifoodplataforma['Tkt.Ent 📍'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_ifoodplataforma['ENTREGA R$_x'] = df_ifoodplataforma['ENTREGA R$_x'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_ifoodplataforma['RETIRA R$_x'] = df_ifoodplataforma['RETIRA R$_x'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_ifoodplataforma['ENTREGA R$_y'] = df_ifoodplataforma['ENTREGA R$_y'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
    df_ifoodplataforma['RETIRA R$_y'] = df_ifoodplataforma['RETIRA R$_y'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))

    df_ifoodplataforma.rename(columns={'ENTREGA R$_x': 'R$ ENT 📍'}, inplace=True)
    df_ifoodplataforma.rename(columns={'RETIRA R$_x': 'R$ RET 📍'}, inplace=True)
    df_ifoodplataforma.rename(columns={'ENTREGA - PEDIDO_x': 'ENTREGA PEDIDO 📍'}, inplace=True)
    df_ifoodplataforma.rename(columns={'RETIRA - PEDIDO_x': 'RETIRA PEDIDO 📍'}, inplace=True)
    df_ifoodplataforma.rename(columns={'Var.R$_Entrega': 'Δ ENTREGA'}, inplace=True)
    df_ifoodplataforma.rename(columns={'ENTREGA R$_y': 'R$ ENT 📅'}, inplace=True)
    df_ifoodplataforma.rename(columns={'RETIRA R$_y': 'R$ RET 📅'}, inplace=True)
    df_ifoodplataforma.rename(columns={'ENTREGA - PEDIDO_y': 'ENTREGA PEDIDO 📅'}, inplace=True)
    df_ifoodplataforma.rename(columns={'RETIRA - PEDIDO_y': 'RETIRA PEDIDO 📅'}, inplace=True)
    df_ifoodplataforma.rename(columns={'Var.R$_Retira': 'Δ RETIRA'}, inplace=True)

    nova_ordem_colunas = ['R$ ENT 📅','R$ ENT 📍','Δ ENTREGA','R$ RET 📅','R$ RET 📍',
                          'Δ RETIRA','ENTREGA PEDIDO 📅','ENTREGA PEDIDO 📍','Δ Pedido.Ent','RETIRA PEDIDO 📅',
                          'RETIRA PEDIDO 📍','Δ Pedido.Ret','Tkt.Ent 📅','Tkt.Ent 📍','Δ Tkt.Ent',
                          'Tkt.Ret 📅','Tkt.Ret 📍','Δ Tkt.Ret']

    df_ifoodplataforma = df_ifoodplataforma[nova_ordem_colunas]
    df_ifoodplataforma1000 = df_ifoodplataforma
    df_ifoodplataforma1000['Δ ENTREGA'] = df_ifoodplataforma1000['Δ ENTREGA'].str.replace('%', '').astype(float)
    df_ifoodplataforma1000['Δ ENTREGA'] = df_ifoodplataforma1000['Δ ENTREGA'].round(2)

    df_ifoodplataforma1001 = df_ifoodplataforma
    df_ifoodplataforma1001['Δ RETIRA'] = df_ifoodplataforma1001['Δ RETIRA'].str.replace('%', '').astype(float)
    df_ifoodplataforma1001['Δ RETIRA'] = df_ifoodplataforma1001['Δ RETIRA'].round(2)

    df_ifoodplataforma1000['Δ Pedido.Ent'] = df_ifoodplataforma1000['Δ Pedido.Ent'].str.replace('%', '').astype(float)
    df_ifoodplataforma1000['Δ Pedido.Ent'] = df_ifoodplataforma1000['Δ Pedido.Ent'].round(2)

    df_ifoodplataforma1000['Δ Pedido.Ret'] = df_ifoodplataforma1000['Δ Pedido.Ret'].str.replace('%', '').astype(float)
    df_ifoodplataforma1000['Δ Pedido.Ret'] = df_ifoodplataforma1000['Δ Pedido.Ret'].round(2)

    df_ifoodplataforma1000['Δ Tkt.Ent'] = df_ifoodplataforma1000['Δ Tkt.Ent'].str.replace('%', '').astype(float)
    df_ifoodplataforma1000['Δ Tkt.Ent'] = df_ifoodplataforma1000['Δ Tkt.Ent'].round(2)

    df_ifoodplataforma1000['Δ Tkt.Ret'] = df_ifoodplataforma1000['Δ Tkt.Ret'].str.replace('%', '').astype(float)
    df_ifoodplataforma1000['Δ Tkt.Ret'] = df_ifoodplataforma1000['Δ Tkt.Ret'].round(2)

    st.divider()

    st.dataframe(
        df_ifoodplataforma1000,
        column_config={
            "Δ ENTREGA": st.column_config.ProgressColumn("Δ ENTREGA", format="%f%%", min_value=0, max_value=100),
            "Δ RETIRA": st.column_config.ProgressColumn("Δ RETIRA", format="%f%%", min_value=0, max_value=100),
            "Δ Pedido.Ent": st.column_config.ProgressColumn("Δ Pedido.Ent", format="%f%%", min_value=0, max_value=100),
            "Δ Pedido.Ret": st.column_config.ProgressColumn("Δ Pedido.Ret",format="%f%%", min_value=0, max_value=100),
            "Δ Tkt.Ent": st.column_config.ProgressColumn("Δ Tkt.Ent", format="%f%%", min_value=0, max_value=100),
            "Δ Tkt.Ret": st.column_config.ProgressColumn("Δ Tkt.Ret", format="%f%%", min_value=0, max_value=100)
        }
    )
    
    st.write("<h3 style='text-align:center;'>Faturamento SM</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric(label = "Faturamento Total",value = controller['TOTAL_SM'])
    col2.metric(label = "Pedidos Totais",value = controller['TOTAL_PEDIDOSM'])
    col3.metric(label = "Tkt.Médio Total",value = controller['TOTAL_TKTSM'])

    st.divider()

    st.dataframe(
        df_smplataforma1000,
        column_config={
            "Δ ENTREGA": st.column_config.ProgressColumn("Δ ENTREGA", format="%f%%", min_value=0, max_value=100),
            "Δ RETIRA": st.column_config.ProgressColumn("Δ RETIRA", format="%f%%", min_value=0, max_value=100),
            "Δ Pedido.Ent": st.column_config.ProgressColumn("Δ Pedido.Ent", format="%f%%", min_value=0, max_value=100),
            "Δ Pedido.Ret": st.column_config.ProgressColumn("Δ Pedido.Ret",format="%f%%", min_value=0, max_value=100),
            "Δ Tkt.Ent": st.column_config.ProgressColumn("Δ Tkt.Ent", format="%f%%", min_value=0, max_value=100),
            "Δ Tkt.Ret": st.column_config.ProgressColumn("Δ Tkt.Ret", format="%f%%", min_value=0, max_value=100)
        }
    )
    return data_inicio,data_fim