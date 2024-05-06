from repositorio import get_excel, get_oracle,get_oracle_periodo,grafico_fat,grafico_fat_1,get_excel_1,grafico_fat_2,Ped_item_tkt
import locale
import pandas as pd
import streamlit as st
from babel import Locale,numbers
from babel.numbers import format_currency
from dateutil.relativedelta import relativedelta

@st.cache_data(experimental_allow_widgets=True,ttl=300)
def controller_vendas(data_inicio, data_fim,flt_mod,status_lj, status_cat):

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    df_filtrado_excel = get_excel(dt_ini=data_inicio, dt_fim=data_fim)
    df_filtrado_oracle = get_oracle(data_inicio=data_inicio, data_fim=data_fim)
    
    meta_venda = df_filtrado_excel.groupby('loja')['META VENDA'].sum()
    meta_venda_total = meta_venda.sum()

    meta_lucratividade = df_filtrado_excel.groupby('loja')['META LUCRATIVIDADE'].sum()
    meta_lucratividade_total = meta_lucratividade.sum()

    meta_lucratividade_total_formatada = locale.currency(meta_lucratividade_total, grouping=True, symbol=True)
    meta_venda_total_formatada = locale.currency(meta_venda_total, grouping=True, symbol=True)

    margem_lucro = (meta_lucratividade_total / meta_venda_total) * 100
    meta_margem_lucro_percent = f'{margem_lucro:.2f}%'

################### TABELA CATEGORIA #####################

    if flt_mod != "Todas":
       df_temp1 = df_filtrado_oracle[df_filtrado_oracle['modalidade'] == flt_mod]
    else:
       df_temp1 = df_filtrado_oracle

    lojas_selecionadas = df_temp1['loja'].unique()

    if status_lj != "Todas":
        df_lojaSF = df_temp1[df_temp1['loja'] == status_lj]
    else:
        df_lojaSF = df_temp1 

    if status_lj != "Todas":
        df_lojaSF_meta = df_filtrado_excel[df_filtrado_excel['loja'] == status_lj]
    else:
        df_lojaSF_meta = df_filtrado_excel

    real_cat1_venda1 = df_lojaSF.groupby('categoriaN1')['valor_pedido'].sum().reset_index()

    meta_cat1_venda1 = df_lojaSF_meta.groupby('N1')['META VENDA'].sum().reset_index()

    df_final = pd.merge(real_cat1_venda1, meta_cat1_venda1, left_on='categoriaN1', right_on='N1', how='outer')
   
    df_final['%'] = ((df_final['valor_pedido'].astype(float) / df_final['META VENDA'].astype(float)) * 100)
    df_final = df_final.sort_values(by='%', ascending=False)
    df_final['%'] = df_final['%'].apply(lambda x: f'{x:.2f} %')

    df_final.drop(columns=['categoriaN1'], inplace=True)

    df_final = df_final[['N1','META VENDA', 'valor_pedido', '%']]

    df_final.reset_index(drop=True, inplace=True)
    df_final.index += 1

    df_final['valor_pedido'] = df_final['valor_pedido'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))
    df_final['META VENDA'] = df_final['META VENDA'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))
    df_final = df_final.rename(columns={"N1": "Categoria","META VENDA": "Meta de Venda ", "valor_pedido":"Venda por Categoria","%":"Performace (%)"})
    
########################## Tabela Produto #################################################

    if status_cat != "Todas":
        df_temp = df_temp1[df_temp1['categoriaN1'] == status_cat]
    else:
        df_temp = df_temp1

    if status_lj != "Todas":
        df_temp = df_temp[df_temp['loja'] == status_lj]

    df_produtoSF = df_temp.groupby(['nome_produto', 'categoriaN1','loja'])['valor_pedido'].sum().reset_index()
    df_produtoSF = df_produtoSF.sort_values(by='valor_pedido', ascending=False)
    sum_prod = df_produtoSF['valor_pedido'].sum()
    sum_prod = float(sum_prod)

    df_produtoSF_grafico = df_temp.groupby('categoriaN1')['valor_pedido'].sum().reset_index()
    df_produtoSF_grafico = df_produtoSF_grafico.sort_values(by='valor_pedido', ascending=False)

    df_produtoSF['%'] = ((df_produtoSF['valor_pedido'].astype(float) / sum_prod) * 100).apply(lambda x: f'{x:.2f} %')

    df_produtoSF.reset_index(drop=True, inplace=True)
    df_produtoSF.index += 1

    df_produtoSF['valor_pedido'] = df_produtoSF['valor_pedido'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))
    df_produtoSF = df_produtoSF.rename(columns={"nome_produto":"Produto","categoriaN1":"Categoria","modalidade":"Plataforma",
                                                "tipo":"Frete","loja":"Loja","valor_pedido":"Venda","%":"Representatividade (%)"})
############################################################################################   
   
    real_venda_total = df_filtrado_oracle['valor_pedido'].sum()
    real_venda_total_formatada = locale.currency(real_venda_total, grouping=True, symbol=True)

    performace_percenttual_de_venda = (float(real_venda_total)/float(meta_venda_total)) * 100
    performace_percenttual_de_venda = f'{performace_percenttual_de_venda:.2f}%'

    df_plat = df_temp.groupby(['nome_produto', 'categoriaN1','modalidade','tipo','loja'])['valor_pedido'].sum().reset_index()

    df_ifood = df_plat[df_plat['modalidade'] == 'IFOOD']['valor_pedido'].sum()
    valores_ifood = locale.currency(df_ifood, grouping=True, symbol=True)

    df_sm = df_plat[df_plat['modalidade'] == 'SM']['valor_pedido'].sum()
    valores_sm = locale.currency(df_sm, grouping=True, symbol=True)

    df_vp = df_plat[df_plat['modalidade'] == 'VIPECOMMERCE']['valor_pedido'].sum()
    valores_vp = locale.currency(df_vp, grouping=True, symbol=True)

    df_ret = df_temp.groupby(['nome_produto', 'categoriaN1','modalidade','tipo','loja'])['valor_pedido'].sum().reset_index()

    df_ifood_r = df_ret[(df_ret['tipo'] == 'R') & (df_ret['modalidade'] == 'IFOOD')]['valor_pedido'].sum()
    valores_ifood_r = locale.currency(df_ifood_r, grouping=True, symbol=True)

    df_sm_r = df_ret[(df_ret['tipo'] == 'R')& (df_ret['modalidade'] == 'SM')]['valor_pedido'].sum()
    valores_sm_r = locale.currency(df_sm_r, grouping=True, symbol=True)

    df_vp_r = df_ret[(df_ret['tipo'] == 'R')& (df_ret['modalidade'] == 'VIPECOMMERCE')]['valor_pedido'].sum()
    valores_vp_r = locale.currency(df_vp_r, grouping=True, symbol=True)
###############
    
    df_ent = df_temp.groupby(['nome_produto', 'categoriaN1','modalidade','tipo','loja'])['valor_pedido'].sum().reset_index()

    df_ifood_e = df_ent[(df_ent['tipo'] == 'E') & (df_ent['modalidade'] == 'IFOOD')]['valor_pedido'].sum()
    valores_ifood_e = locale.currency(df_ifood_e, grouping=True, symbol=True)

    df_sm_e = df_ent[(df_ent['tipo'] == 'E')& (df_ent['modalidade'] == 'SM')]['valor_pedido'].sum()
    valores_sm_e = locale.currency(df_sm_e, grouping=True, symbol=True)

    df_vp_e = df_ent[(df_ent['tipo'] == 'E')& (df_ent['modalidade'] == 'VIPECOMMERCE')]['valor_pedido'].sum()
    valores_vp_e = locale.currency(df_vp_e, grouping=True, symbol=True)

    df_total_sm_ifd_e = df_sm_e + df_ifood_e + df_vp_e
    df_total_sm_ifd_em = locale.currency(df_total_sm_ifd_e, grouping=True, symbol=True)

    df_total_sm_ifd_r = df_sm_r + df_ifood_r + df_vp_r
    df_total_sm_ifd_rm = locale.currency(df_total_sm_ifd_r, grouping=True, symbol=True)

    df_total_sm_ifd = df_total_sm_ifd_e + df_total_sm_ifd_r
    df_total_sm_ifdm = locale.currency(df_total_sm_ifd, grouping=True, symbol=True)

    df_repre_plat = (df_total_sm_ifd/real_venda_total)*100
    df_repre_plat = f'{df_repre_plat:.2f}%'

    df_temp['valor_pedido'] = pd.to_numeric(df_temp['valor_pedido'], errors='coerce')

    unique_values = df_temp['valor_pedido'].unique()

    df_temp.dropna(subset=['valor_pedido'], inplace=True)
    
    top_10_produtos = df_temp.groupby('nome_produto')['valor_pedido'].sum().nlargest(10).reset_index()
    top_10_produtos.index = top_10_produtos.index + 1
    top_10_produtos['valor_pedido'] = top_10_produtos['valor_pedido'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))
    top_10_produtos = top_10_produtos.rename(columns={'nome_produto':'Produto','valor_pedido':'Venda'})

    top_10_categorias = df_temp.groupby('categoriaN1')['valor_pedido'].sum().nlargest(10).reset_index()
    top_10_categorias.index = top_10_categorias.index + 1
    top_10_categorias['valor_pedido'] = top_10_categorias['valor_pedido'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))
    top_10_categorias = top_10_categorias.rename(columns={'categoriaN1':'Categoria','valor_pedido':'Venda'})

    top_10_lojas = df_temp.groupby('loja')['valor_pedido'].sum().nlargest(10).reset_index()
    top_10_lojas.index = top_10_lojas.index + 1
    top_10_lojas['valor_pedido'] = top_10_lojas['valor_pedido'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))
    top_10_lojas = top_10_lojas.rename(columns={'loja':'Loja','valor_pedido':'Venda'})

    return {
        "meta_lucratividade_total_formatada": meta_lucratividade_total_formatada,
        "meta_venda_total_formatada": meta_venda_total_formatada,
        "meta_margem_lucro_percent": meta_margem_lucro_percent,
        "Realizado Total de Venda": real_venda_total_formatada,
        "tabela": df_final.fillna("-"),
        "teste":performace_percenttual_de_venda,
        "teste1":df_produtoSF.fillna("-"),
        "Ifood":valores_ifood,
        "SM":valores_sm,
        "VIP":valores_vp,
        "Ent_SM":valores_sm_e,
        "Ret_SM":valores_sm_r,
        "Ent_Ifood":valores_ifood_e,
        "Ret_Ifood":valores_ifood_r,
        "Ent_VP":valores_vp_e,
        "Ret_VP":valores_vp_r,
        "Total_smifd_r":df_total_sm_ifd_rm,
        "Total_smifd_e":df_total_sm_ifd_em,
        "Total_plat":df_total_sm_ifdm,
        "Repre_plat":df_repre_plat,
        "Top_loja":top_10_lojas,
        "Top_prod":top_10_produtos,
        "Top_cat":top_10_categorias,
        "lj_selecionada":lojas_selecionadas,
        "vend_total_atual":real_venda_total,
        "flt_mod":flt_mod,
        "status_lj":status_lj,
        "status_cat":status_cat,
        "grafico":df_produtoSF_grafico
    }

@st.cache_data(experimental_allow_widgets=True,ttl=300)
def controle_vendas_comparativo(flt_mod, status_lj, status_cat, data_fimp=None, data_iniciop=None):
    # Obtendo os dados do Oracle para o período especificado
    df_filtrado_oracle_periodo = get_oracle_periodo(data_fimp=data_fimp, data_iniciop=data_iniciop)

    # Calculando o total de vendas realizadas no período especificado
    real_venda_totalp = df_filtrado_oracle_periodo['valor_pedido'].sum()

    # Formatando o total de vendas realizadas no período especificado
    real_venda_total_formatadap = locale.currency(real_venda_totalp, grouping=True, symbol=True)


    # modalidade_selecionadas = df_filtrado_oracle_periodo['modalidade'].unique()

    # modalidade_selecionadas = ["Todas"] + modalidade_selecionadas.tolist()

    # flt_mod = st.sidebar.selectbox("Selecione a Plataforma", modalidade_selecionadas)

        # Fazer o filtro apenas se uma categoria específica for selecionada
    if flt_mod != "Todas":
        df_temp1 = df_filtrado_oracle_periodo[df_filtrado_oracle_periodo['modalidade'] == flt_mod]
    else:
        df_temp1 = df_filtrado_oracle_periodo

     # Definir a lista de lojas únicas como todas selecionadas por padrão
    # lojas_selecionadas = df_temp1['loja'].unique()

    # # Adicionar uma opção "Todas" para representar todas as categorias
    # lojas_selecionadas = ["Todas"] + lojas_selecionadas.tolist()

    # # Criar o seletor na barra lateral
    # status_lj = st.sidebar.selectbox("Selecione a Loja:", lojas_selecionadas)

    # Fazer o filtro apenas se uma lojas específica for selecionada
    if status_lj != "Todas":
        df_lojaSF = df_temp1[df_temp1['loja'] == status_lj]
    else:
        df_lojaSF = df_temp1  # Mantém o DataFrame completo se "Todas" for selecionado

    # Agrupando valores por categoria em função da meta venda
    real_cat1_venda1 = df_lojaSF.groupby('categoriaN1')['valor_pedido'].sum().reset_index()
    
########################## Tabela Produto #################################################
        # Definir a lista de categorias únicas como todas selecionadas por padrão
    # categorias_selecionadas = df_temp1['categoriaN1'].unique()

    # # Adicionar uma opção "Todas" para representar todas as categorias
    # categorias_selecionadas = ["Todas"] + categorias_selecionadas.tolist()

    # # Criar o seletor na barra lateral
    # status_cat = st.sidebar.selectbox("Selecione a categoria:", categorias_selecionadas)

        # Fazer o filtro apenas se uma categoria específica for selecionada
    if status_cat != "Todas":
        df_temp = df_temp1[df_temp1['categoriaN1'] == status_cat]
    else:
        df_temp = df_temp1

    # Aplicar filtro da loja, se aplicável
    if status_lj != "Todas":
        df_temp = df_temp[df_temp['loja'] == status_lj]

    # Agrupando valores por categoria em função da meta venda
    df_produtoSF = df_temp.groupby(['nome_produto', 'categoriaN1','modalidade','tipo','loja'])['valor_pedido'].sum().reset_index()
    df_produtoSF['tipo'] = df_produtoSF['tipo'].map({'E': 'ENTREGA', 'R': 'RETIRA'})
    sum_prod = df_produtoSF['valor_pedido'].sum()
    sum_prod = float(sum_prod)

    # Calcular a porcentagem e adicionar como uma nova coluna
    
    df_produtoSF['%'] = ((df_produtoSF['valor_pedido'].astype(float) / sum_prod) * 100).apply(lambda x: f'{x:.2f} %')

    # Resetar o índice começando por 1
    df_produtoSF.reset_index(drop=True, inplace=True)
    df_produtoSF.index += 1

    # Aplicar a formatação monetária nas colunas relevantes
    df_produtoSF['valor_pedido'] = df_produtoSF['valor_pedido'].apply(lambda x: locale.currency(x, grouping=True, symbol=True))
############################################################################################   

    # Filtrar o DataFrame para incluir apenas linhas onde a coluna 'tipo' seja 'SM' ou 'IFOOD'

    df_plat = df_temp.groupby(['nome_produto', 'categoriaN1','modalidade','tipo','loja'])['valor_pedido'].sum().reset_index()

    # Filtrar o DataFrame para as linhas onde a coluna 'modalidade' é igual a 'Ifood'
    df_ifood = df_plat[df_plat['modalidade'] == 'IFOOD']['valor_pedido'].sum()
    valores_ifoodp = locale.currency(df_ifood, grouping=True, symbol=True)

       # Filtrar o DataFrame para as linhas onde a coluna 'modalidade' é igual a 'Ifood'
    df_sm = df_plat[df_plat['modalidade'] == 'SM']['valor_pedido'].sum()
    valores_smp = locale.currency(df_sm, grouping=True, symbol=True)

       # Filtrar o DataFrame para as linhas onde a coluna 'modalidade' é igual a 'Ifood'
    df_vp = df_plat[df_plat['modalidade'] == 'VIPECOMMERCE']['valor_pedido'].sum()
    valores_vpp = locale.currency(df_vp, grouping=True, symbol=True)

    df_ret = df_temp.groupby(['nome_produto', 'categoriaN1','modalidade','tipo','loja'])['valor_pedido'].sum().reset_index()

    # Filtrar o DataFrame para as linhas onde a coluna 'modalidade' é igual a 'Ifood'
    df_ifood_r = df_ret[(df_ret['tipo'] == 'R') & (df_ret['modalidade'] == 'IFOOD')]['valor_pedido'].sum()
    valores_ifood_rp = locale.currency(df_ifood_r, grouping=True, symbol=True)

       # Filtrar o DataFrame para as linhas onde a coluna 'modalidade' é igual a 'Ifood'
    df_sm_r = df_ret[(df_ret['tipo'] == 'R')& (df_ret['modalidade'] == 'SM')]['valor_pedido'].sum()
    valores_sm_rp = locale.currency(df_sm_r, grouping=True, symbol=True)

    # Filtrar o DataFrame para as linhas onde a coluna 'modalidade' é igual a 'Ifood'
    df_vp_r = df_ret[(df_ret['tipo'] == 'R')& (df_ret['modalidade'] == 'VIPECOMMERCE')]['valor_pedido'].sum()
    valores_vp_rp = locale.currency(df_vp_r, grouping=True, symbol=True)
###############
    
    df_ent = df_temp.groupby(['nome_produto', 'categoriaN1','modalidade','tipo','loja'])['valor_pedido'].sum().reset_index()

    # Filtrar o DataFrame para as linhas onde a coluna 'modalidade' é igual a 'Ifood'
    df_ifood_e = df_ent[(df_ent['tipo'] == 'E') & (df_ent['modalidade'] == 'IFOOD')]['valor_pedido'].sum()
    valores_ifood_ep = locale.currency(df_ifood_e, grouping=True, symbol=True)

       # Filtrar o DataFrame para as linhas onde a coluna 'modalidade' é igual a 'Ifood'
    df_sm_e = df_ent[(df_ent['tipo'] == 'E')& (df_ent['modalidade'] == 'SM')]['valor_pedido'].sum()
    valores_sm_ep = locale.currency(df_sm_e, grouping=True, symbol=True)

       # Filtrar o DataFrame para as linhas onde a coluna 'modalidade' é igual a 'Ifood'
    df_vp_e = df_ent[(df_ent['tipo'] == 'E')& (df_ent['modalidade'] == 'VIPECOMMERCE')]['valor_pedido'].sum()
    valores_vp_ep = locale.currency(df_vp_e, grouping=True, symbol=True)

    df_total_sm_ifd_e = df_sm_e + df_ifood_e + df_vp_e
    df_total_sm_ifd_emp = locale.currency(df_total_sm_ifd_e, grouping=True, symbol=True)

    df_total_sm_ifd_r = df_sm_r + df_ifood_r + df_vp_r
    df_total_sm_ifd_rmp = locale.currency(df_total_sm_ifd_r, grouping=True, symbol=True)

    df_total_sm_ifd = df_total_sm_ifd_e + df_total_sm_ifd_r
    df_total_sm_ifdmp = locale.currency(df_total_sm_ifd, grouping=True, symbol=True)

    df_repre_plat = (df_total_sm_ifd/real_venda_totalp)*100
    df_repre_plat = f'{df_repre_plat:.2f}%'

    df_temp['valor_pedido'] = pd.to_numeric(df_temp['valor_pedido'], errors='coerce')

    # Removendo linhas com valores não numéricos em 'valor_pedido'
    df_temp = df_temp.dropna(subset=['valor_pedido'])

    return {
        "real_venda_total_formatadap": real_venda_total_formatadap,
        "vend_total_periodo":real_venda_totalp,
        "Ifoodp": valores_ifoodp,
        "SMp":valores_smp,
        "VPp":valores_vpp,
        "total_plat":df_total_sm_ifdmp,
        "ent_Vpp":valores_vp_ep,
        "ent_ifoodp":valores_ifood_ep,
        "ent_SM":valores_sm_ep,
        "ret_Vpp":valores_vp_rp,
        "ret_ifoodp":valores_ifood_rp,
        "ret_smp":valores_sm_rp,
        "total_entp":df_total_sm_ifd_emp,
        "total_retp":df_total_sm_ifd_rmp
    }

@st.cache_data(experimental_allow_widgets=True,ttl=300)
def controller_faturamento(data_inicio, data_fim):
    # Define a localidade para o Brasil
    locale = Locale('pt', 'BR')

    df_filtrado_oracle = get_oracle(data_inicio=data_inicio, data_fim=data_fim)

    TOTAL_FATSFF = df_filtrado_oracle['valor_pedido'].astype(float).sum()
    teste1000 = TOTAL_FATSFF
    TOTAL_FATSF = numbers.format_currency(TOTAL_FATSFF, 'BRL', locale=locale)

    TOTAL_PEDIDO = df_filtrado_oracle['pedido'].nunique()

    TOTAL_TKT = TOTAL_FATSFF/TOTAL_PEDIDO
    TOTAL_TKT = numbers.format_currency(TOTAL_TKT, 'BRL', locale=locale)
#########################################################################################################################
    
    TOTAL_IFOODSF = df_filtrado_oracle[df_filtrado_oracle['modalidade'] == 'IFOOD']['valor_pedido'].astype(float).sum()
    TOTAL_IFOOD = numbers.format_currency(TOTAL_IFOODSF, 'BRL', locale=locale)

    TOTAL_PEDIDOIFOOD = df_filtrado_oracle[df_filtrado_oracle['modalidade'] == 'IFOOD']['pedido'].nunique()
    
    TOTAL_TKTIFD = TOTAL_IFOODSF/TOTAL_PEDIDOIFOOD
    TOTAL_TKTIFOOD = numbers.format_currency(TOTAL_TKTIFD, 'BRL', locale=locale)
#########################################################################################################################   
    
    locale = Locale('pt', 'BR')  # Definir locale antes de usá-lo

    TOTAL_SMSF = df_filtrado_oracle[df_filtrado_oracle['modalidade'] == 'SM']['valor_pedido'].astype(float).sum()
    TOTAL_SM = numbers.format_currency(TOTAL_SMSF, 'BRL', locale=locale)

    TOTAL_PEDIDOSM = df_filtrado_oracle[df_filtrado_oracle['modalidade'] == 'SM']['pedido'].nunique()

    TOTAL_TKTISM1 = TOTAL_SMSF / TOTAL_PEDIDOSM
    TOTAL_TKTSM = numbers.format_currency(TOTAL_TKTISM1, 'BRL', locale=locale)

    df_filtrado_oracle = get_oracle(data_fim=data_fim, data_inicio=data_inicio)

    grafico = df_filtrado_oracle.groupby('data_pedido')['valor_pedido'].sum().reset_index

    df_filtrado_oracle['tipo'] = df_filtrado_oracle['tipo'].map({'E': 'ENTREGA', 'R': 'RETIRA'})

    df_tipo_E = df_filtrado_oracle[df_filtrado_oracle['tipo'] == 'RETIRA']

    soma_pedidos_por_loja = df_tipo_E.groupby('loja')['pedido'].nunique()

    df_plataforma = df_filtrado_oracle.groupby(['modalidade', 'tipo', 'loja'])['valor_pedido'].sum().reset_index()

    df_plataforma = df_plataforma.rename(columns={'loja': 'Loja', 'valor_pedido': 'Venda', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    df_plataforma = pd.pivot_table(df_plataforma, values='Venda', index=['Plataforma', 'Loja'], columns='Modalidade', aggfunc='sum')

    df_plataforma['ENTREGA'] = df_plataforma['ENTREGA'].fillna(0).astype(int)
    df_plataforma['RETIRA'] = df_plataforma['RETIRA'].fillna(0).astype(int)
    df_plataforma['Total'] = df_plataforma['ENTREGA'] + df_plataforma['RETIRA']

    df_total_por_loja = df_plataforma.groupby(level='Loja').sum()

    df_plataforma['ENTREGA'] = df_plataforma['ENTREGA'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_plataforma['RETIRA'] = df_plataforma['RETIRA'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_plataforma['Total'] = df_plataforma['Total'].apply(lambda x: format_currency(x, 'BRL', locale=locale))

##############################################11111111111111111######################################
    
    df_filtrado_oracle1 = get_oracle(data_fim=data_fim, data_inicio=data_inicio)
  
    df_filtrado_oracle1['tipo'] = df_filtrado_oracle1['tipo'].map({'E': 'ENTREGA', 'R': 'RETIRA'})

    df_tipo_RETIRA = df_filtrado_oracle1[df_filtrado_oracle1['tipo'] == 'RETIRA']

    soma_pedidos_por_loja = df_tipo_RETIRA.groupby('loja')['pedido'].nunique()

    df_plataforma1 = df_filtrado_oracle1.groupby(['modalidade', 'tipo', 'loja'])['pedido'].nunique().reset_index()

    df_plataforma1 = df_plataforma1.rename(columns={'loja': 'Loja', 'pedido': 'Pedidos', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    df_plataforma1 = pd.pivot_table(df_plataforma1, values='Pedidos', index=['Plataforma', 'Loja'], columns='Modalidade', aggfunc='sum')

    df_plataforma1['ENTREGA'] = df_plataforma1['ENTREGA'].fillna(0).astype(int)
    df_plataforma1['RETIRA'] = df_plataforma1['RETIRA'].fillna(0).astype(int)
    df_plataforma1['Total'] = df_plataforma1['ENTREGA'] + df_plataforma1['RETIRA']

    df_total_por_loja = df_plataforma1.groupby(level='Loja').sum()

    teste = df_plataforma1[df_plataforma1.index.get_level_values('Plataforma') == 'IFOOD']

    df_ifoodplataforma = df_plataforma[df_plataforma.index.get_level_values('Plataforma') == 'IFOOD']

    df_ifoodplataforma = pd.merge(df_ifoodplataforma, teste, left_index=True, right_index=True)

    df_ifoodplataforma['ENTREGA_x'] = df_ifoodplataforma['ENTREGA_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)

    df_ifoodplataforma['ENTREGA_y'] = df_ifoodplataforma['ENTREGA_y'].replace({'R$': '', '.': '', ',': '.'}, regex=True).astype(float)

    df_ifoodplataforma['RETIRA_x'] = df_ifoodplataforma['RETIRA_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)

    df_ifoodplataforma['RETIRA_y'] = df_ifoodplataforma['RETIRA_y'].replace({'R$': '', '.': '', ',': '.'}, regex=True).astype(float)

    df_ifoodplataforma['Tkt.Med.Ent'] = df_ifoodplataforma['ENTREGA_x'] / df_ifoodplataforma['ENTREGA_y']
    df_ifoodplataforma['Tkt.Med.Ret'] = df_ifoodplataforma['RETIRA_x'] / df_ifoodplataforma['RETIRA_y']

    df_ifoodplataforma.rename(columns={'Tkt.Med.Ent': 'Tkt.Med.Ent'}, inplace=True)
    df_ifoodplataforma.rename(columns={'RETIRA_y': 'RETIRA - PEDIDO'}, inplace=True)
    df_ifoodplataforma.rename(columns={'ENTREGA_y': 'ENTREGA - PEDIDO'}, inplace=True)
    df_ifoodplataforma.rename(columns={'Tkt.Med.Ret': 'Tkt.Med.Ret'}, inplace=True)
    df_ifoodplataforma.rename(columns={'RETIRA_x': 'RETIRA R$'}, inplace=True)
    df_ifoodplataforma.rename(columns={'ENTREGA_x': 'ENTREGA R$'}, inplace=True)

    df_ifoodplataforma['Tkt.Med.Ent']= df_ifoodplataforma['Tkt.Med.Ent'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_ifoodplataforma['Tkt.Med.Ret']= df_ifoodplataforma['Tkt.Med.Ret'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_ifoodplataforma['ENTREGA R$']= df_ifoodplataforma['ENTREGA R$'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_ifoodplataforma['RETIRA R$']= df_ifoodplataforma['RETIRA R$'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_ifoodplataforma['ENTREGA - PEDIDO'] = df_ifoodplataforma['ENTREGA - PEDIDO'].astype(int)
    df_ifoodplataforma['RETIRA - PEDIDO'] = df_ifoodplataforma['RETIRA - PEDIDO'].astype(int)

    # Criando a lista com a ordem desejada das colunas
    nova_ordem_colunas = ['ENTREGA R$', 'ENTREGA - PEDIDO','Tkt.Med.Ent' ,'RETIRA R$','RETIRA - PEDIDO','Tkt.Med.Ret']

    # Reorganizando as colunas do DataFrame na nova ordem
    df_ifoodplataforma = df_ifoodplataforma[nova_ordem_colunas]
#############111111111111111111111111###############
######################################2222222222222222222######################################
    df_filtrado_oracle2 = get_oracle(data_fim=data_fim, data_inicio=data_inicio)

    df_filtrado_oracle2['tipo'] = df_filtrado_oracle2['tipo'].map({'E': 'ENTREGA', 'R': 'RETIRA'})

    df_tipo_RETIRAsm = df_filtrado_oracle2[df_filtrado_oracle2['tipo'] == 'RETIRA']

    soma_pedidos_por_loja_sm = df_tipo_RETIRAsm.groupby('loja')['pedido'].nunique()

    df_plataforma2 = df_filtrado_oracle2.groupby(['modalidade', 'tipo', 'loja'])['pedido'].nunique().reset_index()

    df_plataforma2 = df_plataforma2.rename(columns={'loja': 'Loja', 'pedido': 'Pedidos', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    df_plataforma2 = pd.pivot_table(df_plataforma2, values='Pedidos', index=['Plataforma', 'Loja'], columns='Modalidade', aggfunc='sum')

    df_plataforma2['ENTREGA'] = df_plataforma2['ENTREGA'].fillna(0).astype(int)
    df_plataforma2['RETIRA'] = df_plataforma2['RETIRA'].fillna(0).astype(int)
    df_plataforma2['Total'] = df_plataforma2['ENTREGA'] + df_plataforma2['RETIRA']

    df_total_por_loja_sm = df_plataforma2.groupby(level='Loja').sum()

    testesm = df_plataforma2[df_plataforma2.index.get_level_values('Plataforma') == 'SM']

    df_smplataforma = df_plataforma[df_plataforma.index.get_level_values('Plataforma') == 'SM']

    df_smplataforma = pd.merge(df_smplataforma, testesm, left_index=True, right_index=True)

#############2222222222222222222###############

    df_filtrado_oracle1 = get_oracle(data_fim=data_fim, data_inicio=data_inicio)

    df_filtrado_oracle1['tipo'] = df_filtrado_oracle1['tipo'].map({'E': 'ENTREGA', 'R': 'RETIRA'})

    df_plataforma1 = df_filtrado_oracle1.groupby(['modalidade', 'tipo', 'loja'])['valor_pedido'].sum().reset_index()

    df_plataforma1 = df_plataforma1.rename(columns={'loja': 'Loja', 'valor_pedido': 'Venda', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    df_plataforma1 = df_plataforma1[df_plataforma1['Plataforma'].isin(['SM', 'IFOOD'])]

    df_plataforma1 = pd.pivot_table(df_plataforma1, values='Venda', index='Loja', columns='Plataforma', aggfunc='sum')

    df_total_por_loja1 = df_plataforma1.groupby(level='Loja').sum()

    #########################

    # df_plataforma500 = df_filtrado_oracle1.groupby(['modalidade', 'loja','data_pedido'])['valor_pedido'].sum().reset_index()

    # df_plataforma500 = df_plataforma500.rename(columns={'loja': 'Loja', 'valor_pedido': 'Venda', 'modalidade': 'Plataforma', 'data_pedido': 'data_pedido'})

    # df_plataforma500 = df_plataforma500[df_plataforma500['Plataforma'].isin(['SM', 'IFOOD'])]

    # df_plataforma500 = pd.pivot_table(df_plataforma500, values='Venda', index='Loja', columns='data_pedido', aggfunc='sum')

    # df_plataforma500 = df_plataforma500.groupby(level='Loja').sum()

    dados40 = grafico_fat()

    df_plataforma500 = dados40.groupby('Periodo')['Valor'].sum().reset_index()
    df_plataforma500 = df_plataforma500.sort_values(by='Valor', ascending=False)

    dados60 = grafico_fat_1()

    df_plataforma600 = dados60.groupby('Periodo')['Valor'].sum().reset_index()
    df_plataforma600 = df_plataforma600.sort_values(by='Valor', ascending=False)

    dados70 = pd.merge(get_excel_1(),grafico_fat_2(),left_index=True, right_index=True)
    
    print(dados70)

    ################

    df_plataforma1['SM'] = df_plataforma1['SM'].fillna(0).astype(int)
    df_plataforma1['IFOOD'] = df_plataforma1['IFOOD'].fillna(0).astype(int)
    df_plataforma1['Total'] = df_plataforma1['SM'] + df_plataforma1['IFOOD']
    
    df_plataforma1['IFOOD'] = df_plataforma1['IFOOD'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_plataforma1['SM'] = df_plataforma1['SM'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_plataforma1['Total'] = df_plataforma1['Total'].apply(lambda x: format_currency(x, 'BRL', locale=locale))



    df_plataforma30 = df_filtrado_oracle1.groupby(['modalidade', 'tipo', 'loja'])['pedido'].nunique().reset_index()

    df_plataforma30 = df_plataforma30.rename(columns={'loja': 'Loja', 'pedido': 'Pedidos', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    df_plataforma30 = df_plataforma30[df_plataforma30['Plataforma'].isin(['SM', 'IFOOD'])]

    df_plataforma30 = pd.pivot_table(df_plataforma30, values='Pedidos', index='Loja', columns='Plataforma', aggfunc='sum')

    df_total_por_loja30 = df_plataforma30.groupby(level='Loja').sum()

    df_plataforma30['SM'] = df_plataforma30['SM'].fillna(0).astype(int)
    df_plataforma30['IFOOD'] = df_plataforma30['IFOOD'].fillna(0).astype(int)
    df_plataforma30['Total'] = df_plataforma30['SM'] + df_plataforma30['IFOOD']

    teste40 = pd.merge(df_plataforma1, df_plataforma30, left_index=True, right_index=True)


    return {
        "SM":df_smplataforma, 
        "Ifood":df_ifoodplataforma,
        "Total":teste40,
        "grafico":df_total_por_loja1,
        'teste':teste,
        "TOTAL_FATSF":TOTAL_FATSF,
        "TOTAL_PEDIDO":TOTAL_PEDIDO,
        "TOTAL_TKT":TOTAL_TKT,
        "TOTAL_IFOOD":TOTAL_IFOOD,
        "TOTAL_PEDIDOIFOOD":TOTAL_PEDIDOIFOOD,
        "TOTAL_TKTIFOOD":TOTAL_TKTIFOOD,
        "TOTAL_SM":TOTAL_SM,
        "TOTAL_PEDIDOSM":TOTAL_PEDIDOSM,
        "TOTAL_TKTSM":TOTAL_TKTSM,
        "teste":teste1000,
        "grafico10":df_plataforma500,
        "grafico11":df_plataforma600,
        "grafico12":dados70



    }

@st.cache_data(experimental_allow_widgets=True,ttl=300)
def controller_faturamento1( data_fimp=None, data_iniciop=None):

    locale = Locale('pt', 'BR')

    df_filtrado_oracle = get_oracle_periodo(data_fimp=data_fimp, data_iniciop=data_iniciop)
    
    df_filtrado_oracle['tipo'] = df_filtrado_oracle['tipo'].map({'E': 'ENTREGA', 'R': 'RETIRA'})

    df_tipo_E = df_filtrado_oracle[df_filtrado_oracle['tipo'] == 'RETIRA']

    soma_pedidos_por_loja = df_tipo_E.groupby('loja')['pedido'].nunique()

    df_plataforma = df_filtrado_oracle.groupby(['modalidade', 'tipo', 'loja'])['valor_pedido'].sum().reset_index()

    df_plataforma = df_plataforma.rename(columns={'loja': 'Loja', 'valor_pedido': 'Venda', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    df_plataforma = pd.pivot_table(df_plataforma, values='Venda', index=['Plataforma', 'Loja'], columns='Modalidade', aggfunc='sum')

    df_plataforma['ENTREGA'] = df_plataforma['ENTREGA'].fillna(0).astype(int)
    df_plataforma['RETIRA'] = df_plataforma['RETIRA'].fillna(0).astype(int)
    df_plataforma['Total'] = df_plataforma['ENTREGA'] + df_plataforma['RETIRA']

    df_total_por_loja = df_plataforma.groupby(level='Loja').sum()

    df_plataforma['ENTREGA'] = df_plataforma['ENTREGA'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_plataforma['RETIRA'] = df_plataforma['RETIRA'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_plataforma['Total'] = df_plataforma['Total'].apply(lambda x: format_currency(x, 'BRL', locale=locale))

##############################################11111111111111111######################################
    
    df_filtrado_oracle1 = get_oracle_periodo(data_fimp=data_fimp, data_iniciop=data_iniciop)
  
    df_filtrado_oracle1['tipo'] = df_filtrado_oracle1['tipo'].map({'E': 'ENTREGA', 'R': 'RETIRA'})

    df_tipo_RETIRA = df_filtrado_oracle1[df_filtrado_oracle1['tipo'] == 'RETIRA']

    soma_pedidos_por_loja = df_tipo_RETIRA.groupby('loja')['pedido'].nunique()

    df_plataforma1 = df_filtrado_oracle1.groupby(['modalidade', 'tipo', 'loja'])['pedido'].nunique().reset_index()

    df_plataforma1 = df_plataforma1.rename(columns={'loja': 'Loja', 'pedido': 'Pedidos', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    df_plataforma1 = pd.pivot_table(df_plataforma1, values='Pedidos', index=['Plataforma', 'Loja'], columns='Modalidade', aggfunc='sum')

    df_plataforma1['ENTREGA'] = df_plataforma1['ENTREGA'].fillna(0).astype(int)
    df_plataforma1['RETIRA'] = df_plataforma1['RETIRA'].fillna(0).astype(int)
    df_plataforma1['Total'] = df_plataforma1['ENTREGA'] + df_plataforma1['RETIRA']

    df_total_por_loja = df_plataforma1.groupby(level='Loja').sum()

    teste = df_plataforma1[df_plataforma1.index.get_level_values('Plataforma') == 'IFOOD']

    df_ifoodplataforma = df_plataforma[df_plataforma.index.get_level_values('Plataforma') == 'IFOOD']

    df_ifoodplataforma = pd.merge(df_ifoodplataforma, teste, left_index=True, right_index=True)

    df_ifoodplataforma['ENTREGA_x'] = df_ifoodplataforma['ENTREGA_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)

    df_ifoodplataforma['ENTREGA_y'] = df_ifoodplataforma['ENTREGA_y'].replace({'R$': '', '.': '', ',': '.'}, regex=True).astype(float)

    df_ifoodplataforma['RETIRA_x'] = df_ifoodplataforma['RETIRA_x'].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)

    df_ifoodplataforma['RETIRA_y'] = df_ifoodplataforma['RETIRA_y'].replace({'R$': '', '.': '', ',': '.'}, regex=True).astype(float)

    df_ifoodplataforma['Tkt.Med.Ent'] = df_ifoodplataforma['ENTREGA_x'] / df_ifoodplataforma['ENTREGA_y']
    df_ifoodplataforma['Tkt.Med.Ret'] = df_ifoodplataforma['RETIRA_x'] / df_ifoodplataforma['RETIRA_y']


    # df_smplataforma = df_plataforma[df_plataforma.index.get_level_values('Plataforma') == 'SM']

    df_ifoodplataforma.rename(columns={'Tkt.Med.Ent': 'Tkt.Med.Ent'}, inplace=True)
    df_ifoodplataforma.rename(columns={'RETIRA_y': 'RETIRA - PEDIDO'}, inplace=True)
    df_ifoodplataforma.rename(columns={'ENTREGA_y': 'ENTREGA - PEDIDO'}, inplace=True)
    df_ifoodplataforma.rename(columns={'Tkt.Med.Ret': 'Tkt.Med.Ret'}, inplace=True)
    df_ifoodplataforma.rename(columns={'RETIRA_x': 'RETIRA R$'}, inplace=True)
    df_ifoodplataforma.rename(columns={'ENTREGA_x': 'ENTREGA R$'}, inplace=True)

    df_ifoodplataforma['Tkt.Med.Ent']= df_ifoodplataforma['Tkt.Med.Ent'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_ifoodplataforma['Tkt.Med.Ret']= df_ifoodplataforma['Tkt.Med.Ret'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_ifoodplataforma['ENTREGA R$']= df_ifoodplataforma['ENTREGA R$'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_ifoodplataforma['RETIRA R$']= df_ifoodplataforma['RETIRA R$'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_ifoodplataforma['ENTREGA - PEDIDO'] = df_ifoodplataforma['ENTREGA - PEDIDO'].astype(int)
    df_ifoodplataforma['RETIRA - PEDIDO'] = df_ifoodplataforma['RETIRA - PEDIDO'].astype(int)

    # Criando a lista com a ordem desejada das colunas
    nova_ordem_colunas = ['ENTREGA R$', 'ENTREGA - PEDIDO','Tkt.Med.Ent' ,'RETIRA R$','RETIRA - PEDIDO','Tkt.Med.Ret']

    # Reorganizando as colunas do DataFrame na nova ordem
    df_ifoodplataforma = df_ifoodplataforma[nova_ordem_colunas]

#############111111111111111111111111###############
    
######################################2222222222222222222######################################
    
    df_filtrado_oracle2 = get_oracle_periodo(data_fimp=data_fimp, data_iniciop=data_iniciop)
    # Mapeando os valores 'E' e 'R' para 'ENTREGA' e 'RETIRA' respectivamente
    df_filtrado_oracle2['tipo'] = df_filtrado_oracle2['tipo'].map({'E': 'ENTREGA', 'R': 'RETIRA'})

    # Filtrando o DataFrame para incluir apenas as linhas onde o valor da coluna 'tipo' é 'RETIRA'
    df_tipo_RETIRAsm = df_filtrado_oracle2[df_filtrado_oracle2['tipo'] == 'RETIRA']

    # Calcular a contagem de valores únicos da coluna 'pedido' por loja
    soma_pedidos_por_loja_sm = df_tipo_RETIRAsm.groupby('loja')['pedido'].nunique()

    # Agrupando os dados e calculando a contagem de valores únicos da coluna 'pedido' por loja
    df_plataforma2 = df_filtrado_oracle2.groupby(['modalidade', 'tipo', 'loja'])['pedido'].nunique().reset_index()

    # Renomeando as colunas
    df_plataforma2 = df_plataforma2.rename(columns={'loja': 'Loja', 'pedido': 'Pedidos', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    # Criando a pivot table para separar as colunas
    df_plataforma2 = pd.pivot_table(df_plataforma2, values='Pedidos', index=['Plataforma', 'Loja'], columns='Modalidade', aggfunc='sum')

    # Adicionando colunas 'ENTREGA' e 'RETIRA' com os totais e convertendo para tipo inteiro
    df_plataforma2['ENTREGA'] = df_plataforma2['ENTREGA'].fillna(0).astype(int)
    df_plataforma2['RETIRA'] = df_plataforma2['RETIRA'].fillna(0).astype(int)
    df_plataforma2['Total'] = df_plataforma2['ENTREGA'] + df_plataforma2['RETIRA']

    # Agrupando o DataFrame por 'Loja' para calcular o total por loja
    df_total_por_loja_sm = df_plataforma2.groupby(level='Loja').sum()

    # Dividindo o DataFrame em dois com base na coluna 'Plataforma'
    testesm = df_plataforma2[df_plataforma2.index.get_level_values('Plataforma') == 'SM']

    df_smplataforma = df_plataforma[df_plataforma.index.get_level_values('Plataforma') == 'SM']

    df_smplataforma = pd.merge(df_smplataforma, testesm, left_index=True, right_index=True)

#############2222222222222222222###############

    df_filtrado_oracle1 = get_oracle(data_fim=data_fimp, data_inicio=data_iniciop)

    df_filtrado_oracle1['tipo'] = df_filtrado_oracle1['tipo'].map({'E': 'ENTREGA', 'R': 'RETIRA'})

    df_plataforma1 = df_filtrado_oracle1.groupby(['modalidade', 'tipo', 'loja'])['valor_pedido'].sum().reset_index()

    df_plataforma1 = df_plataforma1.rename(columns={'loja': 'Loja', 'valor_pedido': 'Venda', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    df_plataforma1 = df_plataforma1[df_plataforma1['Plataforma'].isin(['SM', 'IFOOD'])]

    df_plataforma1 = pd.pivot_table(df_plataforma1, values='Venda', index='Loja', columns='Plataforma', aggfunc='sum')

    df_total_por_loja1 = df_plataforma1.groupby(level='Loja').sum()

    df_plataforma1['SM'] = df_plataforma1['SM'].fillna(0).astype(int)
    df_plataforma1['IFOOD'] = df_plataforma1['IFOOD'].fillna(0).astype(int)
    df_plataforma1['Total'] = df_plataforma1['SM'] + df_plataforma1['IFOOD']
    
    df_plataforma1['IFOOD'] = df_plataforma1['IFOOD'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_plataforma1['SM'] = df_plataforma1['SM'].apply(lambda x: format_currency(x, 'BRL', locale=locale))
    df_plataforma1['Total'] = df_plataforma1['Total'].apply(lambda x: format_currency(x, 'BRL', locale=locale))



    df_plataforma30 = df_filtrado_oracle1.groupby(['modalidade', 'tipo', 'loja'])['pedido'].nunique().reset_index()

    df_plataforma30 = df_plataforma30.rename(columns={'loja': 'Loja', 'pedido': 'Pedidos', 'modalidade': 'Plataforma', 'tipo': 'Modalidade'})

    df_plataforma30 = df_plataforma30[df_plataforma30['Plataforma'].isin(['SM', 'IFOOD'])]

    df_plataforma30 = pd.pivot_table(df_plataforma30, values='Pedidos', index='Loja', columns='Plataforma', aggfunc='sum')

    df_total_por_loja30 = df_plataforma30.groupby(level='Loja').sum()

    df_plataforma30['SM'] = df_plataforma30['SM'].fillna(0).astype(int)
    df_plataforma30['IFOOD'] = df_plataforma30['IFOOD'].fillna(0).astype(int)
    df_plataforma30['Total'] = df_plataforma30['SM'] + df_plataforma30['IFOOD']

    teste40 = pd.merge(df_plataforma1, df_plataforma30, left_index=True, right_index=True)

    return {
        "SM":df_smplataforma, 
        "Ifood":df_ifoodplataforma, 
        "Total":teste40,
        "grafico":df_total_por_loja1,
        'teste':teste
    }

@st.cache_data(experimental_allow_widgets=True,ttl=300)
def Vendas_ano(data_fim,data_inicio,periodo):

    # data_fimp = data_fim
    # data_iniciop = data_inicio
    # periodo = periodo

    if periodo == "Ano" or "Mês":
        # Definir data llllfinal como a data atual menos um dia
        data_fimp = data_fim - relativedelta(years=1)
        # Definir data inicial como um ano antes da data final
        data_iniciop = data_inicio - relativedelta(years=1)

    banco = get_oracle_periodo(data_fimp,data_iniciop)
    banco = banco['valor_pedido'].sum()
    banco = locale.currency(banco, grouping=True, symbol=True)

    return{"Venda_ano_passado":banco}

@st.cache_data(experimental_allow_widgets=True,ttl=300)
def Vendas_mês(data_fim,data_inicio,periodo):

    data_fimp = data_fim
    data_iniciop = data_inicio
    periodo = periodo

    if periodo == "Ano" or "Mês":
        # Definir data llllfinal como a data atual menos um dia
        data_fimp = data_fim - relativedelta(month=1)
        # Definir data inicial como um ano antes da data final
        data_iniciop = data_inicio - relativedelta(month=1)

    banco = get_oracle_periodo(data_fimp,data_iniciop)
    banco = banco['valor_pedido'].sum()
    banco = locale.currency(banco, grouping=True, symbol=True)

    return{"Venda_mês_passado":banco}

def ped_item(data_inicio, data_fim):

    df_filtrado_ped_item = Ped_item_tkt(data_inicio=data_inicio, data_fim=data_fim)
    
    Item = df_filtrado_ped_item['media_itens_por_pedido'].sum()
    Item = round(Item, 2)
    Pedido = df_filtrado_ped_item['qtd_pedidos'].sum()
    tkt = df_filtrado_ped_item['tkt_medio'].sum()
    tkt = locale.currency(tkt, grouping=True, symbol=True)
    


    return{"Itens":Item,
           "Pedido":Pedido,
           "tkt":tkt}