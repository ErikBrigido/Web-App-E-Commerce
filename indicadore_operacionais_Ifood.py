import pandas as pd
import streamlit as st
import locale
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
# warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)

def extract_columns_with_nps(df):
    columns_with_nps = []

    for column in df.columns:
        if any('NPS' in str(cell) for cell in df[column]):
            columns_with_nps.append(column)

    df_with_nps_columns = df[[df.columns[0]] + columns_with_nps]
    df_with_nps_columns.iloc[3:, 1:] = df_with_nps_columns.iloc[3:, 1:].applymap(pd.to_numeric, errors='coerce').applymap(lambda x: round(x, 0) if not pd.isnull(x) else x)
    pd.options.display.float_format = '{:,.0f}'.format
    df_with_nps_columns.iloc[2] = pd.to_datetime(df_with_nps_columns.iloc[2], errors='coerce', format='%d/%m/%Y').dt.strftime('%d/%m/%Y')
    
    return df_with_nps_columns

# Caminho completo até o arquivo Excel
file_path = r'C:\Users\Erik.Brigido\OneDrive - nagumo.com.br\ECOMMERCE\BI\Acompanhamento KPIs Nagumo (7).xlsx'

# Carregar o arquivo Excel especificando a planilha
df = pd.read_excel(file_path, sheet_name='KPIs Semana (Trimestre 1)')

df_with_nps_columns = extract_columns_with_nps(df)

indices_to_drop = list(range(0, 2)) + [3] + list(range(5, 27)) + list(range(52, 55))
df_with_nps_columns = df_with_nps_columns.drop(df_with_nps_columns.index[indices_to_drop])

selected_columns = [df_with_nps_columns.columns[0]] + list(df_with_nps_columns.columns[-9:])
selected_df = df_with_nps_columns[selected_columns]

numeric_df = selected_df.iloc[2:].apply(pd.to_numeric, errors='coerce')
mean_row = numeric_df.mean()
mean_row.rename = 'Média'

df_with_mean = pd.concat([selected_df, mean_row.to_frame().T])

new_header = df_with_mean.iloc[0]
df_with_mean = df_with_mean[1:]

table_data = []
for _, row in df_with_mean.iterrows():
    table_data.append({new_header[col]: row[col] for col in df_with_mean.columns})

####################################################

def extract_columns_with_gmv(df):
    columns_with_nps = []

    for column in df.columns:
        if any('GMV' in str(cell) for cell in df[column]):
            columns_with_nps.append(column)

    df_with_nps_columns = df[[df.columns[0]] + columns_with_nps]
    df_with_nps_columns.iloc[3:, 1:] = df_with_nps_columns.iloc[3:, 1:].applymap(pd.to_numeric, errors='coerce').applymap(lambda x: round(x, 0) if not pd.isnull(x) else x)
    pd.options.display.float_format = '{:,.0f}'.format
    df_with_nps_columns.iloc[2] = pd.to_datetime(df_with_nps_columns.iloc[2], errors='coerce', format='%d/%m/%Y').dt.strftime('%d/%m/%Y')
    
    return df_with_nps_columns

df_with_nps_columns = extract_columns_with_gmv(df)

indices_to_drop = list(range(0, 2)) + [3] + list(range(5, 27)) + list(range(52, 55))
df_with_nps_columns = df_with_nps_columns.drop(df_with_nps_columns.index[indices_to_drop])

selected_columns = [df_with_nps_columns.columns[0]] + list(df_with_nps_columns.columns[-9:])
selected_df = df_with_nps_columns[selected_columns]

numeric_df = selected_df.iloc[2:].apply(pd.to_numeric, errors='coerce')
mean_row = numeric_df.mean()
mean_row.rename = 'Média'

df_with_mean = pd.concat([selected_df, mean_row.to_frame().T])

new_header = df_with_mean.iloc[0]
df_with_mean = df_with_mean[1:]

table_data_GMV = []
for _, row in df_with_mean.iterrows():
    table_data_GMV.append({new_header[col]: row[col] for col in df_with_mean.columns})

#######################

def extract_columns_with_sla(df):
    columns_with_sla = []

    for column in df.columns:
        if any('SLA Separação' in str(cell) for cell in df[column]):
            columns_with_sla.append(column)

    df_with_sla_columns = df[[df.columns[0]] + columns_with_sla]
    df_with_sla_columns.iloc[3:, 1:] = df_with_sla_columns.iloc[3:, 1:].applymap(pd.to_numeric, errors='coerce')
    pd.options.display.float_format = '{:,.2f}'.format
    df_with_sla_columns.iloc[2] = pd.to_datetime(df_with_sla_columns.iloc[2], errors='coerce', format='%d/%m/%Y').dt.strftime('%d/%m/%Y')
    
    return df_with_sla_columns

df_with_sla_columns = extract_columns_with_sla(df)

indices_to_drop = list(range(0, 2)) + [3] + list(range(5, 27)) + list(range(52, 55))
df_with_sla_columns = df_with_sla_columns.drop(df_with_sla_columns.index[indices_to_drop])

selected_columns = [df_with_sla_columns.columns[0]] + list(df_with_sla_columns.columns[-9:])
selected_df = df_with_sla_columns[selected_columns]

numeric_df = selected_df.iloc[2:].apply(pd.to_numeric, errors='coerce')
mean_row = numeric_df.mean()
mean_row.rename = 'Média'

df_with_mean = pd.concat([selected_df, mean_row.to_frame().T])

df_with_mean.iloc[1:, 1:] = df_with_mean.iloc[1:, 1:].applymap(lambda x: '{:.2f}%'.format(x * 100) if pd.notnull(x) else x)

new_header = df_with_mean.iloc[0]
df_with_mean = df_with_mean[1:]

table_data_sla = []
for _, row in df_with_mean.iterrows():
    table_data_sla.append({new_header[col]: row[col] for col in df_with_mean.columns})

##################


def extract_columns_with_app(df):
    columns_with_app = []

    for column in df.columns:
        if any('% app separador' in str(cell) for cell in df[column]):
            columns_with_app.append(column)

    df_with_app_columns = df[[df.columns[0]] + columns_with_app]
    df_with_app_columns.iloc[3:, 1:] = (df_with_app_columns.iloc[3:, 1:].applymap(pd.to_numeric, errors='coerce'))
    pd.options.display.float_format = '{:,.2f}'.format
    df_with_app_columns.iloc[2] = pd.to_datetime(df_with_app_columns.iloc[2], errors='coerce', format='%d/%m/%Y').dt.strftime('%d/%m/%Y')
    
    return df_with_app_columns

df_with_app_columns = extract_columns_with_app(df)

indices_to_drop = list(range(0, 2)) + [3] + list(range(5, 27)) + list(range(52, 55))
df_with_app_columns = df_with_app_columns.drop(df_with_app_columns.index[indices_to_drop])

selected_columns = [df_with_app_columns.columns[0]] + list(df_with_app_columns.columns[-9:])
selected_df = df_with_app_columns[selected_columns]

numeric_df = selected_df.iloc[2:].apply(pd.to_numeric, errors='coerce')
mean_row = numeric_df.mean()
mean_row.rename = 'Média'

df_with_mean = pd.concat([selected_df, mean_row.to_frame().T])

df_with_mean.iloc[1:, 1:] = df_with_mean.iloc[1:, 1:].applymap(lambda x: '{:.2f}%'.format(x * 100) if pd.notnull(x) else x)

new_header = df_with_mean.iloc[0]
df_with_mean = df_with_mean[1:]

table_data_app = []
for _, row in df_with_mean.iterrows():
    table_data_app.append({new_header[col]: row[col] for col in df_with_mean.columns})

    ######################

def extract_columns_with_ruptura(df):
    columns_with_ruptura = []

    for column in df.columns:
        if any('Taxa de Ruptura' in str(cell) for cell in df[column]):
            columns_with_ruptura.append(column)

    df_with_ruptura_columns = df[[df.columns[0]] + columns_with_ruptura]
    df_with_ruptura_columns.iloc[3:, 1:] = (df_with_ruptura_columns.iloc[3:, 1:].applymap(pd.to_numeric, errors='coerce'))
    pd.options.display.float_format = '{:,.2f}'.format
    df_with_ruptura_columns.iloc[2] = pd.to_datetime(df_with_ruptura_columns.iloc[2], errors='coerce', format='%d/%m/%Y').dt.strftime('%d/%m/%Y')
    
    return df_with_ruptura_columns

df_with_ruptura_columns = extract_columns_with_ruptura(df)

indices_to_drop = list(range(0, 2)) + [3] + list(range(5, 27)) + list(range(52, 55))
df_with_ruptura_columns = df_with_ruptura_columns.drop(df_with_ruptura_columns.index[indices_to_drop])

selected_columns = [df_with_ruptura_columns.columns[0]] + list(df_with_ruptura_columns.columns[-9:])
selected_df = df_with_ruptura_columns[selected_columns]

numeric_df = selected_df.iloc[2:].apply(pd.to_numeric, errors='coerce')
mean_row = numeric_df.mean()
mean_row.rename = 'Média'

df_with_mean = pd.concat([selected_df, mean_row.to_frame().T])

df_with_mean.iloc[1:, 1:] = df_with_mean.iloc[1:, 1:].applymap(lambda x: '{:.2f}%'.format(x * 100) if pd.notnull(x) else x)

new_header = df_with_mean.iloc[0]
df_with_mean = df_with_mean[1:]

table_data_ruptura = []
for _, row in df_with_mean.iterrows():
    table_data_ruptura.append({new_header[col]: row[col] for col in df_with_mean.columns})


#################

def extract_columns_with_canc(df):
    columns_with_canc = []

    for column in df.columns:
        if any('Taxa de Cancelamento' in str(cell) for cell in df[column]):
            columns_with_canc.append(column)

    df_with_canc_columns = df[[df.columns[0]] + columns_with_canc]
    df_with_canc_columns.iloc[3:, 1:] = (df_with_canc_columns.iloc[3:, 1:].applymap(pd.to_numeric, errors='coerce'))
    pd.options.display.float_format = '{:,.02}'.format
    df_with_canc_columns.iloc[2] = pd.to_datetime(df_with_canc_columns.iloc[2], errors='coerce', format='%d/%m/%Y').dt.strftime('%d/%m/%Y')
    
    return df_with_canc_columns

df_with_canc_columns = extract_columns_with_canc(df)

indices_to_drop = list(range(0, 2)) + [3] + list(range(5, 27)) + list(range(52, 55))
df_with_canc_columns = df_with_canc_columns.drop(df_with_canc_columns.index[indices_to_drop])

selected_columns = [df_with_canc_columns.columns[0]] + list(df_with_canc_columns.columns[-9:])
selected_df = df_with_canc_columns[selected_columns]

numeric_df = selected_df.iloc[2:].apply(pd.to_numeric, errors='coerce')
mean_row = numeric_df.mean()
mean_row.rename = 'Média'

df_with_mean = pd.concat([selected_df, mean_row.to_frame().T])

df_with_mean.iloc[1:, 1:] = df_with_mean.iloc[1:, 1:].applymap(lambda x: '{:.2f}%'.format(x * 100) if pd.notnull(x) else x)

new_header = df_with_mean.iloc[0]
df_with_mean = df_with_mean[1:]

table_data_canc = []
for _, row in df_with_mean.iterrows():
    table_data_canc.append({new_header[col]: row[col] for col in df_with_mean.columns})

warnings.resetwarnings()



