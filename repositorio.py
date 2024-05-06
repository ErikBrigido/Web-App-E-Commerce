import pandas as pd
from datetime import datetime, timedelta
from connection import ConexaoOracleC5
from sqlalchemy import text
import streamlit as st
from dateutil.relativedelta import relativedelta

def get_excel(dt_ini = None, dt_fim = None):

    # # Filtrar por período de análise
    # if dt_fim is None:
    #     dt_fim = datetime.now() - timedelta(days=7)
    # if dt_ini is None: 
    #     dt_ini = dt_fim - timedelta(days=7)

    #Converter as datas de início e fim para datetime
    dt_ini = datetime.combine(dt_ini, datetime.min.time())
    dt_fim = datetime.combine(dt_fim, datetime.max.time())
        
    # Leitura dos metas | arquivo xlsx na rede Ecommerce
    df = pd.read_excel(r'META 2024_ECOMMERCE_VF2.xlsx', sheet_name='BASE DIARIZADA')
    st.session_state["data"] = df

    # Tratamento dos formatos dos dados das colunas | Substituindo pontos e vírgulas quando necessário
    df['META VENDA'] = df['META VENDA'].replace(',', '', regex=True).astype(float)
    df['META LUCRATIVIDADE'] = df['META LUCRATIVIDADE'].replace(',', '', regex=True).astype(float)

    # Converter a coluna 'DATA' para datetime
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%y')

    # Filtrar o DataFrame com base nas datas selecionadas
    df_filtrado = df[
        (df['DATA'] >= dt_ini) & (df['DATA'] <= dt_fim)]
    
    return df_filtrado

def get_oracle(data_inicio, data_fim):
    with ConexaoOracleC5() as session:

        query = text(f"""SELECT vend.dtapedidoafv AS data_pedido,
            cli.NROEMPRESA AS loja,
            prod.DESCCOMPLETA AS nome_produto,
            cat.categoriaN1,
            cat.categoriaN2,
            cat.categoriaN3,
            vend.nropedcliente AS pedido,
            cli.nomerazao AS cliente,
            ite.qtdpedida AS quantidade,
            epv.PEDIDOID AS Modalidade,
            epv.INDENTREGARETIRA AS tipo,
            ROUND(SUM(ite.qtdpedida * ite.vlrembtabpreco), 2) AS valor_pedido,
            LPAD(cli.nrocgccpf || cli.digcgccpf, 11, '0') AS cpf
        FROM consinco.ecomm_pdv_item ite
            LEFT JOIN consinco.ecomm_pdv_venda vend ON vend.seqedipedvenda = ite.seqedipedvenda
            LEFT JOIN consinco.ecomm_pdv_cliente cli ON cli.nropedidoafv = ite.seqedipedvenda
            LEFT JOIN consinco.map_produto prod ON prod.seqproduto = ite.seqproduto
            LEFT JOIN consinco.etlv_categoria cat ON prod.seqfamilia = cat.seqfamilia
            left join consinco.ECOMM_PDV_VENDA epv ON epv.SEQEDIPEDVENDA  = ite.SEQEDIPEDVENDA
        WHERE vend.statuspedido IN ('L', 'N', 'F') AND
                    vend.DTAPEDIDOAFV >=  TO_DATE('{data_inicio}', 'YYYY-MM-DD') AND 
                    vend.DTAPEDIDOAFV <=  TO_DATE('{data_fim}', 'YYYY-MM-DD')
        GROUP BY vend.dtapedidoafv, cat.categoriaN1, cat.categoriaN2, cat.categoriaN3, vend.nropedcliente, cli.nomerazao,
                    ite.qtdpedida, ite.vlrembtabpreco, cli.nrocgccpf , cli.DIGCGCCPF, prod.DESCCOMPLETA, cli.NROEMPRESA, epv.PEDIDOID, epv.INDENTREGARETIRA
        ORDER BY 7, 1
            """)

        dados = session.execute(query).fetchall()
        
        nomes_colunas = ['data_pedido', 'loja', 'nome_produto', 'categoriaN1', 'categoriaN2', 'categoriaN3', 
                    'pedido', 'cliente', 'quantidade', 'modalidade','tipo','valor_pedido', 'cpf']

        dados = pd.DataFrame.from_records(dados, columns=nomes_colunas)

        st.session_state["data1"] =  dados
        
    return dados

def get_oracle_periodo(data_iniciop=None, data_fimp=None):
    with ConexaoOracleC5() as session:
        # Converter as datas para strings no formato 'YYYY-MM-DD'
        data_inicio_str = data_iniciop.strftime('%Y-%m-%d')
        data_fim_str = data_fimp.strftime('%Y-%m-%d')

        # Construir a consulta SQL usando parâmetros
        query = text("""
            SELECT vend.dtapedidoafv AS data_pedido,
                cli.NROEMPRESA AS loja,
                prod.DESCCOMPLETA AS nome_produto,
                cat.categoriaN1,
                cat.categoriaN2,
                cat.categoriaN3,
                vend.nropedcliente AS pedido,
                cli.nomerazao AS cliente,
                ite.qtdpedida AS quantidade,
                epv.PEDIDOID AS Modalidade,
                epv.INDENTREGARETIRA AS tipo,
                ROUND(SUM(ite.qtdpedida * ite.vlrembtabpreco), 2) AS valor_pedido,
                LPAD(cli.nrocgccpf || cli.digcgccpf, 11, '0') AS cpf
            FROM consinco.ecomm_pdv_item ite
                LEFT JOIN consinco.ecomm_pdv_venda vend ON vend.seqedipedvenda = ite.seqedipedvenda
                LEFT JOIN consinco.ecomm_pdv_cliente cli ON cli.nropedidoafv = ite.seqedipedvenda
                LEFT JOIN consinco.map_produto prod ON prod.seqproduto = ite.seqproduto
                LEFT JOIN consinco.etlv_categoria cat ON prod.seqfamilia = cat.seqfamilia
                left join consinco.ECOMM_PDV_VENDA epv ON epv.SEQEDIPEDVENDA  = ite.SEQEDIPEDVENDA
            WHERE vend.statuspedido IN ('L', 'F','N') AND
                vend.DTAPEDIDOAFV >=  TO_DATE(:data_inicio, 'YYYY-MM-DD') AND 
                vend.DTAPEDIDOAFV <=  TO_DATE(:data_fim, 'YYYY-MM-DD')
            GROUP BY vend.dtapedidoafv, cat.categoriaN1, cat.categoriaN2, cat.categoriaN3, vend.nropedcliente, cli.nomerazao,
                ite.qtdpedida, ite.vlrembtabpreco, cli.nrocgccpf , cli.DIGCGCCPF, prod.DESCCOMPLETA, cli.NROEMPRESA, epv.PEDIDOID, epv.INDENTREGARETIRA
            ORDER BY 7, 1
        """)

        # Executar a consulta SQL substituindo os parâmetros pelas datas formatadas
        dados = session.execute(query, {'data_inicio': data_inicio_str, 'data_fim': data_fim_str}).fetchall()
        
        # Definir os nomes das colunas
        nomes_colunas = ['data_pedido', 'loja', 'nome_produto', 'categoriaN1', 'categoriaN2', 'categoriaN3', 
                    'pedido', 'cliente', 'quantidade', 'modalidade','tipo','valor_pedido', 'cpf']

        # Criar um DataFrame pandas a partir dos dados obtidos
        dados = pd.DataFrame.from_records(dados, columns=nomes_colunas)

        # Armazenar os dados na sessão do Streamlit
        st.session_state["data1"] = dados
        
    return dados

def get_oracle_cupom(data_inicio=None, data_fim=None):
    with ConexaoOracleC5() as session:
        # Converter as datas para strings no formato 'YYYY-MM-DD'
        data_inicio_str = data_inicio.strftime('%Y-%m-%d')
        data_fim_str = data_fim.strftime('%Y-%m-%d')

        # Construir a consulta SQL usando parâmetros
        query = text("""
                    SELECT
                        NROEMPRESA AS LOJA,
                        NROPEDIDOAFV AS Pedido,
                        DESCTIPOACRESCDESCTO AS CUPOM,
                        pag.VALOR AS VALOR,
                        VLRTOTFRETE AS ValorCupom,
                        INDENTREGARETIRA,
                        CASE
                            WHEN PAG.NROFORMAPAGTO = 81 THEN 'VOUCHER MARKETING NAGUMO'
                            WHEN PAG.NROFORMAPAGTO = 65 THEN 'VOUCHER SITE MERCADO'
                            ELSE NULL -- Adicione outras condições aqui se necessário
                        END AS FORMA_PAGAMENTO
                    FROM CONSINCO.ECOMM_PDV_VENDA epv
                    LEFT JOIN consinco.ecomm_pdv_pagto pag ON pag.SEQEDIPEDVENDA = epv.SEQEDIPEDVENDA
                    WHERE DESCTIPOACRESCDESCTO IS NOT NULL AND
                        epv.DTAPEDIDOAFV >= TO_DATE(:data_inicio, 'YYYY-MM-DD') AND
                        epv.DTAPEDIDOAFV <= TO_DATE(:data_fim, 'YYYY-MM-DD')
                    GROUP BY NROPEDIDOAFV, NROEMPRESA, DESCTIPOACRESCDESCTO, pag.VALOR, VLRTOTFRETE, INDENTREGARETIRA, PAG.NROFORMAPAGTO
        """)

        # Executar a consulta SQL substituindo os parâmetros pelas datas formatadas
        dados = session.execute(query, {'data_inicio': data_inicio_str, 'data_fim': data_fim_str}).fetchall()
        
        # Definir os nomes das colunas
        nomes_colunas = ['LOJA','PEDIDO','CUPOM','VALOR','VALORCUPOM','INDENTREGARETIRA','FORMA_PAGAMENTO']

        # Criar um DataFrame pandas a partir dos dados obtidos
        dados = pd.DataFrame.from_records(dados, columns=nomes_colunas)

        # Armazenar os dados na sessão do Streamlit
        st.session_state["data1"] = dados
        
    return dados

def grafico_fat():
        with ConexaoOracleC5() as session:
            query = text("""
                            SELECT TO_CHAR(epv.DTAPEDIDOAFV, 'YYYY-MM') AS Ano_Mês,
                                SUM(epp.VALOR) AS Total_Valor
                            FROM consinco.ECOMM_PDV_PAGTO epp
                            LEFT JOIN CONSINCO.ECOMM_PDV_VENDA epv ON epv.SEQEDIPEDVENDA = epp.SEQEDIPEDVENDA
                            WHERE epv.DTAPEDIDOAFV >= TRUNC(SYSDATE, 'MM') - INTERVAL '12' MONTH  -- Primeiro dia do mês atual menos 10 meses
                            AND epv.DTAPEDIDOAFV <= TRUNC(SYSDATE)  -- Último dia do mês atual
                            GROUP BY TO_CHAR(epv.DTAPEDIDOAFV, 'YYYY-MM')
                            ORDER BY TO_DATE(TO_CHAR(epv.DTAPEDIDOAFV, 'YYYY-MM'), 'YYYY-MM')
                        """)
            
        dados = session.execute(query).fetchall()
        
        nomes_colunas = ['Periodo','Valor']
        
        dados = pd.DataFrame.from_records(dados, columns=nomes_colunas)

        st.session_state["data1"] = dados
    
        return dados

def grafico_fat_1():
        with ConexaoOracleC5() as session:
            query = text("""
                        WITH vendas AS (
                            SELECT TO_CHAR(epv.DTAPEDIDOAFV, 'YYYY-MM') AS Ano_Mês,
                                SUM(epp.VALOR) AS Total_Valor,
                                ROW_NUMBER() OVER (ORDER BY TO_DATE(TO_CHAR(epv.DTAPEDIDOAFV, 'YYYY-MM'), 'YYYY-MM') DESC) AS rn
                            FROM consinco.ECOMM_PDV_PAGTO epp
                            LEFT JOIN CONSINCO.ECOMM_PDV_VENDA epv ON epv.SEQEDIPEDVENDA = epp.SEQEDIPEDVENDA
                            WHERE epv.DTAPEDIDOAFV >= ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -12)
                            GROUP BY TO_CHAR(epv.DTAPEDIDOAFV, 'YYYY-MM')
                        )
                        SELECT Ano_Mês,
                            Total_Valor
                        FROM vendas
                        WHERE rn = 1 OR rn = (SELECT MAX(rn) FROM vendas)
                        ORDER BY TO_DATE(Ano_Mês, 'YYYY-MM') DESC
                        """)
            
        dados = session.execute(query).fetchall()
        
        nomes_colunas = ['Periodo','Valor']
        
        dados = pd.DataFrame.from_records(dados, columns=nomes_colunas)

        st.session_state["data1"] = dados
    
        return dados

def grafico_fat_2():
        with ConexaoOracleC5() as session:
            query = text("""
                         WITH vendas AS (
                            SELECT TO_CHAR(epv.DTAPEDIDOAFV, 'YYYY-MM') AS Ano_Mês,
                                SUM(epp.VALOR) AS Total_Valor
                            FROM consinco.ECOMM_PDV_PAGTO epp
                            LEFT JOIN CONSINCO.ECOMM_PDV_VENDA epv ON epv.SEQEDIPEDVENDA = epp.SEQEDIPEDVENDA
                            WHERE epv.DTAPEDIDOAFV >= ADD_MONTHS(TRUNC(SYSDATE), -1)
                            GROUP BY TO_CHAR(epv.DTAPEDIDOAFV, 'YYYY-MM')
                        )
                        SELECT Ano_Mês,
                            Total_Valor,
                            LAG(Total_Valor) OVER (ORDER BY TO_DATE(Ano_Mês, 'YYYY-MM')) AS Total_Valor_Anterior
                        FROM vendas
                        ORDER BY TO_DATE(Ano_Mês, 'YYYY-MM') DESC
                        FETCH FIRST 2 ROWS ONLY
                        """)
            
        dados = session.execute(query).fetchall()
        
        nomes_colunas = ['Periodo','Valor','Valor1']
        
        dados = pd.DataFrame.from_records(dados, columns=nomes_colunas)

        st.session_state["data1"] = dados
    
        return dados

def get_excel_1():
    # Carregar o arquivo Excel em um DataFrame
    df = pd.read_excel(r'META 2024_ECOMMERCE_VF2.xlsx', sheet_name='BASE DIARIZADA')

    # Remover vírgulas e converter para float
    df['META VENDA'] = df['META VENDA'].replace(',', '', regex=True).astype(float)

    # Converter a coluna 'DATA' para o formato datetime
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%y')

    # Extrair o mês atual
    mes_atual = pd.Timestamp.now().month

    # Filtrar apenas as linhas do mês atual
    df_mes_atual = df[df['DATA'].dt.month == mes_atual]

    # Somar os valores da coluna 'META VENDA' para o mês atual
    meta_venda_mes_atual = df_mes_atual['META VENDA'].sum()

    # Criar um DataFrame com o mês atual e a soma da 'META VENDA'
    df_resultado = pd.DataFrame({'Mês': [mes_atual], 'Meta_Venda': [meta_venda_mes_atual]})

    return df_resultado

def Ped_item_tkt(data_inicio, data_fim):
    with ConexaoOracleC5() as session:
        query = text(f"""
                SELECT 
                    total_info.total_valor,
                    total_info.qtd_pedidos,
                    total_info.tkt_medio,
                    items_info.media_itens_por_pedido
                FROM (
                    SELECT 
                        SUM(epp.VALOR) AS total_valor,
                        COUNT(vend.SEQEDIPEDVENDA) AS qtd_pedidos,
                        SUM(epp.VALOR) / COUNT(vend.SEQEDIPEDVENDA) AS tkt_medio
                    FROM 
                        CONSINCO.ECOMM_PDV_PAGTO epp
                    LEFT JOIN 
                        CONSINCO.ECOMM_PDV_VENDA vend ON vend.SEQEDIPEDVENDA = epp.SEQEDIPEDVENDA
                    WHERE 
                        vend.DTAPEDIDOAFV >= TO_DATE('{data_inicio}', 'YYYY-MM-DD') AND 
                        vend.DTAPEDIDOAFV <= TO_DATE('{data_fim}', 'YYYY-MM-DD')
                ) total_info,
                (
                    SELECT AVG(items_per_order) AS media_itens_por_pedido
                    FROM (
                        SELECT 
                            epi.SEQEDIPEDVENDA, 
                            COUNT(epi.SEQPEDVENDAITEM) AS items_per_order
                        FROM 
                            CONSINCO.ECOMM_PDV_ITEM epi
                        LEFT JOIN CONSINCO.ECOMM_PDV_VENDA epv ON epv.SEQEDIPEDVENDA = epi.SEQEDIPEDVENDA
                        WHERE 
                        epv.DTAPEDIDOAFV >= TO_DATE('{data_inicio}', 'YYYY-MM-DD') AND 
                        epv.DTAPEDIDOAFV <= TO_DATE('{data_fim}', 'YYYY-MM-DD')
                        GROUP BY 
                            epi.SEQEDIPEDVENDA
                    )
                ) items_info
                """)
    
        dados = session.execute(query).fetchall()
            
        nomes_colunas = ['total_valor','qtd_pedidos','tkt_medio',"media_itens_por_pedido"]
            
        dados = pd.DataFrame.from_records(dados, columns=nomes_colunas)

        st.session_state["data1"] = dados
    
    return dados