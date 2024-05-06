from repositorio import get_oracle_cupom, get_oracle
import streamlit as st
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
def cupom():

       # Definindo o estilo CSS para os cards editáveis
    with open('card_css.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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

    st.markdown("<div class='nunito-header'>Cupons vs Retorno</div>", unsafe_allow_html=True)

    data_inicio = st.sidebar.date_input("Selecione a data de início")
    data_fim = st.sidebar.date_input("Selecione a data de fim")

    if data_fim < data_inicio:
     st.warning("A data de fim não pode ser menor que a data de início. Por favor, selecione uma data de fim posterior à data de início.",icon="⚠️")
     st.stop()

    dados = get_oracle_cupom(data_inicio=data_inicio,data_fim=data_fim)

    flt_cupom = dados['CUPOM'].unique()
    flt_LJ = dados['LOJA'].unique()

    flt_cupom = ["Todas"] + flt_cupom.tolist()
    flt_LJ = ["Todas"] + flt_LJ.tolist()

    flt_cupom_sidebar = st.sidebar.selectbox("Selecione um Cupom", flt_cupom)
    flt_LJ_sidebar = st.sidebar.selectbox("Selecione uma Loja", flt_LJ)

    if flt_cupom_sidebar != "Todas":
        dados_temp = dados[dados['CUPOM'] == flt_cupom_sidebar]
    else:
        dados_temp = dados

    if flt_LJ_sidebar != "Todas":
        dados_10 = dados_temp[dados_temp['LOJA'] == flt_LJ_sidebar]
    else:
        dados_10 = dados_temp

    dados1 = dados_10[dados_10['FORMA_PAGAMENTO'].notnull()]
    dados1 = dados1.drop(columns=['VALORCUPOM'])
    dados1['INDENTREGARETIRA'] = dados1['INDENTREGARETIRA'].map({'E': 'ENTREGA', 'R': 'RETIRA'})

    valor_total_cupons = dados1['VALOR'].sum()
    valor_total_cupons_float = float(valor_total_cupons)
    valor_total_cupons_float = locale.currency(valor_total_cupons_float, grouping=True, symbol=True)

    qntd_Cupom = dados1['CUPOM'].count()

    dados2 = dados_10[dados_10['FORMA_PAGAMENTO'].isnull()]
    total_vend_com_cupom = dados2['VALOR'].sum()
    total_vend_com_cupom = float(total_vend_com_cupom)
    total_vend_com_cupom = locale.currency(total_vend_com_cupom, grouping=True, symbol=True)

    top_10_qntd_cupom = dados1.groupby('LOJA')['CUPOM'].count().nlargest(10).reset_index()
    top_10_qntd_cupom.index = top_10_qntd_cupom.index + 1

    dados1['VALOR'] = dados1['VALOR'].astype(float)
    top_10_valores_cupom = dados1.groupby('CUPOM')['VALOR'].sum().nlargest(10).reset_index()
    top_10_valores_cupom.index = top_10_valores_cupom.index + 1
    top_10_valores_cupom['VALOR'] = top_10_valores_cupom['VALOR'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))

    dados2['VALOR'] = dados2['VALOR'].astype(float)
    top_10_compras_cupom = dados2.groupby('LOJA')['VALOR'].sum().nlargest(10).reset_index()
    top_10_compras_cupom.index = top_10_compras_cupom.index + 1
    top_10_compras_cupom['VALOR'] = top_10_compras_cupom['VALOR'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))

    total_vend_com_cupom_nagumo = dados1.loc[dados1['FORMA_PAGAMENTO'] == 'VOUCHER MARKETING NAGUMO', 'VALOR'].sum()
    total_vend_com_cupom_nagumo_QTD = dados1.loc[dados1['FORMA_PAGAMENTO'] == 'VOUCHER MARKETING NAGUMO', 'CUPOM'].count()

    total_vend_com_cupom_mercado = dados1.loc[dados1['FORMA_PAGAMENTO'] == 'VOUCHER SITE MERCADO', 'VALOR'].sum()
    total_vend_com_cupom_mercado_QTD = dados1.loc[dados1['FORMA_PAGAMENTO'] == 'VOUCHER SITE MERCADO', 'CUPOM'].count()

    total_vend_com_cupom_nagumo = float(total_vend_com_cupom_nagumo)
    total_vend_com_cupom_nagumo_formatado = locale.currency(total_vend_com_cupom_nagumo, grouping=True, symbol=True)
    total_vend_com_cupom_mercado = float(total_vend_com_cupom_mercado)
    total_vend_com_cupom_mercado_formatado = locale.currency(total_vend_com_cupom_mercado, grouping=True, symbol=True)

    dados1['VALOR'] = dados1['VALOR'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))

    VENDA_TOTAIS_ECOMM = get_oracle(data_fim=data_fim,data_inicio=data_inicio)
    VENDA_TOTAIS_ECOMM =  VENDA_TOTAIS_ECOMM ['valor_pedido'].sum()
    VENDA_TOTAIS_ECOMM = float(VENDA_TOTAIS_ECOMM)
    total_vend_com_cupom1 = total_vend_com_cupom.replace("R$", "").replace(".", "").replace(",", ".")
    total_vend_com_cupom1 = float(total_vend_com_cupom1)
    var = (total_vend_com_cupom1 / VENDA_TOTAIS_ECOMM * 100)
    var_formatted = f'{var:.2f} %'
    VENDA_TOTAIS_ECOMM = locale.currency(VENDA_TOTAIS_ECOMM, grouping=True, symbol=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label = "Valor total Cupons",value = valor_total_cupons_float)
    col2.metric(label = "Quantidade total Cupons",value = qntd_Cupom)
    col3.metric(label = "Total Vendas Ecomm",value = VENDA_TOTAIS_ECOMM)
    col4.metric(label = "Total Vendas Ecomm com Cupom",value = total_vend_com_cupom,delta=var_formatted)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label = "VOUCHER NAGUMO - Qtd",value = total_vend_com_cupom_nagumo_QTD)
    col2.metric(label = "VOUCHER NAGUMO - R$",value = total_vend_com_cupom_nagumo_formatado)
    col3.metric(label = "VOUCHER SITE MERCADO - Qtd",value = total_vend_com_cupom_mercado_QTD)
    col4.metric(label = "VOUCHER SITE MERCADO - R$",value = total_vend_com_cupom_mercado_formatado)

    st.divider()
    

    st.write("<h3 style='text-align:center;'>Rankings</h3>", unsafe_allow_html=True)

    col1, col2, col3= st.columns(3)

    with col1:
        st.write("<h3 style='text-align:center;'>Top 10 Quantidade Cupom</h3>", unsafe_allow_html=True)
        st.table(top_10_qntd_cupom.style.set_properties(**{'border-bottom': '1px solid rgba(2, 2, 2, 0.1)', 'border-right': '1px solid rgba(2, 2, 2, 0.1)', 'vertical-align': 'middle', 'padding': '0.25rem 0.375rem', 'font-weight': '400', 'font-size': '12px'}))

    with col2:
        st.write("<h3 style='text-align:center;'>Top 10 valores cupons</h3>", unsafe_allow_html=True)
        st.table(top_10_valores_cupom.style.set_properties(**{'border-bottom': '1px solid rgba(2, 2, 2, 0.1)', 'border-right': '1px solid rgba(2, 2, 2, 0.1)', 'vertical-align': 'middle', 'padding': '0.25rem 0.375rem', 'font-weight': '400', 'font-size': '12px'}))
    with col3:
        st.write("<h3 style='text-align:center;'>Top 10 compras com cupons</h3>", unsafe_allow_html=True)
        st.table(top_10_compras_cupom.style.set_properties(**{'border-bottom': '1px solid rgba(2, 2, 2, 0.1)', 'border-right': '1px solid rgba(2, 2, 2, 0.1)', 'vertical-align': 'middle', 'padding': '0.25rem 0.375rem', 'font-weight': '400', 'font-size': '12px'}))

    st.divider()
        # st.table(controller["tabela"])
    st.table(dados1.style.set_table_styles([{
    'selector': 'thead th', 
    'props': [
        ('background-color', '#062952'), 
        ('color', 'white')  # Cor do texto
    ]
}]))

    return data_fim, data_inicio