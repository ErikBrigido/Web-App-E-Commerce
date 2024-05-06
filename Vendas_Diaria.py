import streamlit as st
from controller import controller_faturamento
from controller import controller_faturamento1
from dateutil.relativedelta import relativedelta
from repositorio import get_oracle,get_excel
import pandas as pd
import locale
from babel import Locale
from babel.numbers import format_currency
import numpy as np
from PIL import Image
import imgkit

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def vendas_diaria():
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
      df_filtrado_excel = get_excel(dt_ini=data_inicio, dt_fim=data_fim)
    
    meta_venda = df_filtrado_excel.groupby('loja')['META VENDA'].sum()
    meta_venda_total = meta_venda.sum()


    st.write("<h3 style='text-align:center;'>Vendas Diaria</h3>", unsafe_allow_html=True)

    valor = controller['teste']
    valor_normalizado = min(max(valor / meta_venda_total, 0), 1)

    st.progress(valor_normalizado)

    prog_perc = valor_normalizado
    prog_perc = f'{prog_perc:.2%}'
   
    st.text(f'Performace em função da meta : {prog_perc}')

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

    total10['TKt 📍'] = total10['Total_x_y']/total10['Total_y_y']
    total10['TKt 📍'] = total10['TKt 📍'].round(2)

    total10['Total_x_x'] = total10['Total_x_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
    total10['TKt 📅'] = total10['Total_x_x']/total10['Total_y_x']
    total10['TKt 📅'] = total10['TKt 📅'].round(2)

    total10['Δ TKT'] = ((total10['TKt 📍']/total10['TKt 📅'])-1)*100
    total10['Δ TKT'] = total10['Δ TKT'].round(2)

    total10['Δ Venda'] = ((total10['Total_x_x']/total10['Total_x_y'])-1)*100
    total10['Δ Venda'] = total10['Δ Venda'].round(2)

    total10['Δ Pedido'] = ((total10['Total_y_x']/total10['Total_y_y'])-1)*100
    total10['Δ Pedido'] = total10['Δ Pedido'].round(2)

    total10 = total10.sort_values(by='Δ Venda', ascending=False)

    total10['Total_x_x'] = total10['Total_x_x'].apply(lambda x: format_currency(x, 'BRL', locale='pt_BR'))
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

    nova_ordem = ['Venda Total 📅','Venda Total 📍','Δ Venda','Pedido Total 📅','Pedido Total 📍','Δ Pedido','TKt 📅','TKt 📍','Δ TKT']

    total10 = total10[nova_ordem]

    st.table(total10.style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', '#062952'), ('color', 'white'), ('text-align', 'center')]},
        {'selector': 'tbody td', 'props': [('text-align', 'center')]}
    ]))

    return data_inicio,data_fim,total10
