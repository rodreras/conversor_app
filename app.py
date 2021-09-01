import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import datetime
import time
import streamlit as st
import traceback
import os, glob, shutil
import base64
import io 

#funcoes
def deletando_pasta(pasta):
    print('Deletando os arquivos')
    shutil.rmtree(pasta)
    os.mkdir(pasta)

#configurando a página
st.set_page_config(page_title = 'MDGeo SHMS Converter')

#carregando a logo
logo = 'MDGEO.jpeg'


#Título e Subtítulo
st.title('MDGeo Apps')
st.subheader('Conversor de Dados do SHMS')


#Introdução 
st.markdown('''
Aplicação desenvolvida pelo Setor de Modelagem da MDGeo com intuito de
facilitar o processamento dos dados da plataforma SHMS. Ao inserir os dados, 
você será capaz de escolher o tipo de instrumento, se deseja concatenar o arquivo todo
ou fazer um filtro de acordo com datas. Para maiores informações, [acesse o manual](https://github.com/rodreras/conversor_app/blob/main/readme.md)

 ''')

#colocando opção de escolha para processamento dos dados

me1, me2 = st.columns(2)
option = me1.radio('Que tipo de dado você quer processar?', ['PZE','PZC', 'INAs','MNA','NR'])
filtro = me2.radio('Você quer baixar os dados filtrados ou completos?', ['Completos','Filtrados'])


if filtro == 'Filtrados':

    min_date = datetime.datetime(2010,1,1)
    max_date = datetime.datetime.today()

    a_date = st.date_input('Escolha uma data', (min_date, max_date))
    ini = pd.to_datetime(a_date[0])
    fim = pd.to_datetime(a_date[1])

    #dando a opção de fazer o upload dos dados
    uploaded_file = st.file_uploader("Escolha um arquivo")

    
    # opção para processar dados do PZC
    if option == 'PZC':
        if uploaded_file is None:
            print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:

            print(st.markdown('''
                         ▶️ Iniciando o processamento dos dados de PZC...\n
                           ▶️ Isso pode levar alguns instantes!
                      '''))

            df = pd.read_excel(uploaded_file, sheet_name=None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names
            deletando_pasta('pzc')
            for index, item in enumerate(sheets):
                try:
                    # fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    # colocando as coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    # aplicando o cabecalho

                    # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]

                    y = x[1] + 1


                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass
                    
                    # remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)

                    # criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte
                    # reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO', 'Data',
                                 'LESTE', 'NORTE',
                                 'LEITURA_SENSOR/DEPTH(m)',
                                 'COTA_LOCAL/ELEVATION(m)',
                                 'MCA/WATER LEVEL(m)']]

                    # salvando em diferentes DFs
                    df_1.to_csv('pzc/df_{}.csv'.format(item), index=False, encoding='utf-8')
                except:
                    pass

            st.write('As planilhas já foram organizadas:')

            path_sc = 'pzc'

            files = glob.glob(path_sc + "/*.csv")  # pegando os arquivos com o seu path

            filename = []  # criando lista vazia
            # criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)
            # lista vazia
            frames = []

            # criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:
                # lendo o arquivo
                df2 = pd.read_csv(arquivo)
                # appending
                frames.append(df2)

            # concatenando todos os arquivos
            df = pd.concat(frames, axis=0, ignore_index=True)
            # transformando a coluna em timeseries do panda
            df['Data'] = pd.to_datetime(df['Data'])
            # criando uma máscara para poder definir as datas de início e fim
            mask = (df['Data'] > ini) & (df['Data'] <= fim)
            # aplicando a máscara
            df = df.loc[mask]

            shape_info = df.shape
            st.write(
                'Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(
                    shape_info[0],
                    shape_info[1],
                    len(frames),
                    (len(frames) / len(sheets)) * 100))

            # mostrando o df modificado
            df
            # salvando o aquivo em apenas um
            df.to_csv('tabela_pzc_concatenada.csv', index=False)

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_PZC_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)

    # opção para processar dados do PZE
    if option == 'PZE':
        if uploaded_file is None:
            print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:

            print(st.markdown('''
                         ▶️ Iniciando o processamento dos dados de PZE...\n
                           ▶️ Isso pode levar alguns instantes!
                      '''))

            df = pd.read_excel(uploaded_file, sheet_name=None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names
            #removendo possiveis arquivos antigos
            deletando_pasta('instrumentos')
            for index, item in enumerate(sheets):
                try:
                    # fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    # colocando coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    # aplicando o cabecalho

                     # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]

                    y = x[1] + 1

                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass

                    # remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)

                    # criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte

                    # reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO',
                                 'Data', 'LESTE', 'NORTE',
                                 'COTA/ELEVATION(m)',
                                 'THERMISTOR/ELECTRICAL RESISTANCE(Ohm)',
                                 'MCA/WATER LEVEL(m)',
                                 'FREQUENCIA/FREQUENCY(Hz)',
                                 'KPA/PRESSURE(kPA)',
                                 'TEMPERATURA/TEMPERATURE(°C)',
                                 'COTA_LOCAL/ELEVATION(m)']]

                    print('Planilha {} feita.'.format(item))

                    # fazer o apêndice de cada df numa df maior.
                    # df_mrn.append(df_1)

                    # salvando em diferentes DFs
                    df_1.to_csv('instrumentos/df_{}.csv'.format(item), index=False, encoding='utf-8')
                except:
                    pass

            # loop para concatenar os arquivos

            path_sc = 'instrumentos'

            files = glob.glob(path_sc + "/*.csv")  # pegando os arquivos com o seu path

            filename = []  # criando lista vazia

            # criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)

            # lista vazia
            frames = []

            # criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:
                print('Concatenando {}'.format(arquivo))
                # lendo o arquivo
                df2 = pd.read_csv(arquivo)

                # appending
                frames.append(df2)
            # concatenando todos os arquivos
            df = pd.concat(frames, axis=0, ignore_index=True)

            # transformando a coluna em timeseries do panda
            df['Data'] = pd.to_datetime(df['Data'])
            # criando uma máscara para poder definir as datas de início e fim
            mask = (df['Data'] > ini) & (df['Data'] <= fim)
            # aplicando a máscara
            df = df.loc[mask]

            shape_info = df.shape
            st.write(
                'Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(
                    shape_info[0],
                    shape_info[1],
                    len(frames),
                    (len(frames) / len(sheets)) * 100))
            # mostrando o df modificado
            df

            # salvando o aquivo em apenas um
            df.to_csv('tabela_pze_concatenada.csv', index=False)

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_PZE_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)

    # opção para processar os dados de INAs
    if option == 'INAs':
        if uploaded_file is None:
            print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:
            print(st.markdown('''
                                     ▶️ Iniciando o processamento dos dados de INA...\n
                                       ▶️ Isso pode levar alguns instantes!
                                  '''))

            df = pd.read_excel(uploaded_file, sheet_name=None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names
            deletando_pasta('inas')
            for index, item in enumerate(sheets):
                try:
                    # fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    # colocando as coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    # aplicando o cabecalho

                     # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]

                    y = x[1] + 1

                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass


                    # remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)

                    # criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte

                    # reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO', 'Data',
                                 'NORTE', 'LESTE',
                                 'MCA/WATER LEVEL(m)',
                                 'COTA_LOCAL/ELEVATION(m)',
                                 'LEITURA_SENSOR/DEPTH(m)']]

                    # formatando a coluna de data
                    df_1['Data'] = pd.to_datetime(df_1['Data'], errors='coerce')

                    #forçando que as colunas que devem ser float fiquem com NaN enquanto for str
                    cols = ['MCA/WATER LEVEL(m)', 'LEITURA_SENSOR/DEPTH(m)', 'COTA_LOCAL/ELEVATION(m)']
                    mask = df_1[cols].applymap(lambda x: isinstance(x, (int, float)))

                    df_1[cols] = df_1[cols].where(mask)

                    print('Planilha {} feita.'.format(item))

                    # fazer o apêndice de cada df numa df maior.
                    # df_mrn.append(df_1)

                    # salvando em diferentes DFs
                    df_1.to_csv('inas/df_{}.csv'.format(item), index=False, encoding='utf-8')
                except:
                    pass

            st.write('As planilhas já foram organizadas:')

            path_sc = 'inas'

            files = glob.glob(path_sc + "/*.csv")  # pegando os arquivos com o seu path

            filename = []  # criando lista vazia
            # criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)
            # lista vazia
            frames = []

            # criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:
                # lendo o arquivo
                df2 = pd.read_csv(arquivo)
                # appending
                frames.append(df2)

            # concatenando todos os arquivos
            df = pd.concat(frames, axis=0, ignore_index=True)
            # transformando a coluna em timeseries do panda
            df['Data'] = pd.to_datetime(df['Data'])
            # criando uma máscara para poder definir as datas de início e fim
            mask = (df['Data'] > ini) & (df['Data'] <= fim)
            # aplicando a máscara
            df = df.loc[mask]

            shape_info = df.shape
            st.write(
                'Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(
                    shape_info[0],
                    shape_info[1],
                    len(frames),
                    (len(frames) / len(sheets)) * 100))

            # mostrando o df modificado
            df
            # salvando o aquivo em apenas um
            df.to_csv('tabela_inas_concatenada.csv', index=False)

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_INA_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)

    #opção para processar dados de NRs
    if option == 'NR':
        if uploaded_file is None:
            print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:
            print(st.markdown('''
                                       ▶️ Iniciando o processamento dos dados de NR...\n
                                         ▶️ Isso pode levar alguns instantes!
                                    '''))
            df = pd.read_excel(uploaded_file, sheet_name=None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names
            deletando_pasta('nr')
            for index, item in enumerate(sheets):
                try:
                    # fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    # colocando as coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    # aplicando o cabecalho

                     # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]
                    y = x[1] + 1

                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass

                    # remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)

                    # criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte

                    # reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO',
                                 'Data',
                                 'NORTE',
                                 'LESTE',
                                 'COTA_LOCAL/ELEVATION(m)']]

                    # formatando a coluna de data
                    df_1['Data'] = pd.to_datetime(df_1['Data'], errors='coerce')

                    # forçando que as colunas que devem ser float fiquem com NaN enquanto for str
                    cols = ['MCA/WATER LEVEL(m)', 'LEITURA_SENSOR/DEPTH(m)', 'COTA_LOCAL/ELEVATION(m)']
                    mask = df_1[cols].applymap(lambda x: isinstance(x, (int, float)))

                    df_1[cols] = df_1[cols].where(mask)

                    print('Planilha {} feita.'.format(item))

                    # fazer o apêndice de cada df numa df maior.
                    # df_mrn.append(df_1)

                    # salvando em diferentes DFs
                    df_1.to_csv('nr/df_{}.csv'.format(item), index=False, encoding='utf-8')
                except:
                    pass
            path_sc = 'nr'

            files = glob.glob(path_sc + "/*.csv")  # pegando os arquivos com o seu path

            filename = []  # criando lista vazia

            # criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)

            # lista vazia
            frames = []

            # criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:
                print('Concatenando {}'.format(arquivo))
                # lendo o arquivo
                df2 = pd.read_csv(arquivo)

                # appending
                frames.append(df2)
            # concatenando todos os arquivos
            df = pd.concat(frames, axis=0, ignore_index=True)

            shape_info = df.shape
            st.write(
                'Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(
                    shape_info[0],
                    shape_info[1],
                    len(frames),
                    (len(frames) / len(sheets)) * 100))

            # transformando a coluna em timeseries do panda
            df['Data'] = pd.to_datetime(df['Data'])
            # criando uma máscara para poder definir as datas de início e fim
            mask = (df['Data'] > ini) & (df['Data'] <= fim)
            # aplicando a máscara
            df = df.loc[mask]
            # mostrando o df modificado
            df

            # salvando o aquivo em apenas um
            df.to_csv('tabela_nr_concatenada.csv', index=False)

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_NR_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)

    #opção para processar dados de MNAs
    if option == 'MNA':
        if uploaded_file is None:
            print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:
            print(st.markdown('''
                                       ▶️ Iniciando o processamento dos dados de MNA...\n
                                         ▶️ Isso pode levar alguns instantes!
                                    '''))
            df = pd.read_excel(uploaded_file, sheet_name=None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names
            deletando_pasta('mna')

            for index, item in enumerate(sheets):
                try:
                    # fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    # colocando as coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    # aplicando o cabecalho

                     # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]
                    y = x[1] + 1

                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass


                    # remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)

                    # criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte

                    # reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO',
                                 'Data',
                                 'NORTE',
                                 'LESTE',
                                 'COTA_LOCAL/ELEVATION(m)',
                                'LEITURA_SENSOR/DEPTH(m)',
                                'MCA/WATER LEVEL(m)']]

                    # formatando a coluna de data
                    df_1['Data'] = pd.to_datetime(df_1['Data'], errors='coerce')

                    # forçando que as colunas que devem ser float fiquem com NaN enquanto for str
                    cols = ['MCA/WATER LEVEL(m)', 'LEITURA_SENSOR/DEPTH(m)', 'COTA_LOCAL/ELEVATION(m)']
                    mask = df_1[cols].applymap(lambda x: isinstance(x, (int, float)))

                    df_1[cols] = df_1[cols].where(mask)

                    print('Planilha {} feita.'.format(item))

                    # fazer o apêndice de cada df numa df maior.
                    # df_mrn.append(df_1)

                    # salvando em diferentes DFs
                    df_1.to_csv('mna/df_{}.csv'.format(item), index=False, encoding='utf-8')
                except:
                    pass
            path_sc = 'mna'

            files = glob.glob(path_sc + "/*.csv")  # pegando os arquivos com o seu path

            filename = []  # criando lista vazia

            # criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)

            # lista vazia
            frames = []

            # criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:
                print('Concatenando {}'.format(arquivo))
                # lendo o arquivo
                df2 = pd.read_csv(arquivo)

                # appending
                frames.append(df2)
            # concatenando todos os arquivos
            df = pd.concat(frames, axis=0, ignore_index=True)

            shape_info = df.shape
            st.write(
                'Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(
                    shape_info[0],
                    shape_info[1],
                    len(frames),
                    (len(frames) / len(sheets)) * 100))

            # transformando a coluna em timeseries do panda
            df['Data'] = pd.to_datetime(df['Data'])
            # criando uma máscara para poder definir as datas de início e fim
            mask = (df['Data'] > ini) & (df['Data'] <= fim)
            # aplicando a máscara
            df = df.loc[mask]
            # mostrando o df modificado
            df

            # salvando o aquivo em apenas um
            df.to_csv('tabela_mna_concatenada.csv', index=False)

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_MNA_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)

if filtro == 'Completos':

    #dando a opção de fazer o upload dos dados
    uploaded_file = st.file_uploader("Escolha um arquivo")


    #opção para processar dados do PZC
    if option == 'PZC':
        if uploaded_file is None:
           print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:

            print(st.markdown('''
                         ▶️ Iniciando o processamento dos dados de PZC...\n
                           ▶️ Isso pode levar alguns instantes!
                      '''))

            df = pd.read_excel(uploaded_file, sheet_name = None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names
            deletando_pasta('pzc')

            for index, item in enumerate(sheets):
                try:
                    #fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    # colocando as coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    #aplicando o cabecalho

                      # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]
                    y = x[1] + 1

                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass


                    #remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)


                    #criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte
                    #reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO','Data',
                                 'LESTE','NORTE',
                                 'LEITURA_SENSOR/DEPTH(m)',
                                 'COTA_LOCAL/ELEVATION(m)',
                                 'MCA/WATER LEVEL(m)']]


                    #salvando em diferentes DFs
                    df_1.to_csv('pzc/df_{}.csv'.format(item), index = False, encoding = 'utf-8')
                except:
                    pass


            st.write('As planilhas já foram organizadas:')

            path_sc = 'pzc'

            files = glob.glob(path_sc + "/*.csv") #pegando os arquivos com o seu path

            filename = [] #criando lista vazia
            #criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)
            #lista vazia
            frames = []

            #criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:

                #lendo o arquivo
                df2 = pd.read_csv(arquivo)
                #appending
                frames.append(df2)

            # concatenando todos os arquivos
            df = pd.concat(frames, axis=0, ignore_index=True)

            shape_info = df.shape
            st.write('Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(shape_info[0],
                                                                                                                                           shape_info[1],
                                                                                                                                           len(frames),
                                                                                                                                            (len(frames)/len(sheets))*100))
            # mostrando o df modificado
            df
            #salvando o aquivo em apenas um
            df.to_csv('tabela_pzc_concatenada.csv', index = False )

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_PZC_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)

    #opção para processar dados do PZE
    if option == 'PZE':
        if uploaded_file is None:
            print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:

            print(st.markdown('''
                         ▶️ Iniciando o processamento dos dados de PZE...\n
                           ▶️ Isso pode levar alguns instantes!
                      '''))

            df =  pd.read_excel(uploaded_file, sheet_name = None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names

            deletando_pasta('instrumentos')

            for index, item in enumerate(sheets):
                try:
                    #fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    #colocando coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    #aplicando o cabecalho

                     # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]

                    y = x[1] + 1
  
                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass
                    
                    #remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)


                    #criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte

                    #reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO',
                                 'Data', 'LESTE', 'NORTE',
                                 'COTA/ELEVATION(m)',
                                 'THERMISTOR/ELECTRICAL RESISTANCE(Ohm)',
                                 'MCA/WATER LEVEL(m)',
                                 'FREQUENCIA/FREQUENCY(Hz)',
                                 'KPA/PRESSURE(kPA)',
                                 'TEMPERATURA/TEMPERATURE(°C)',
                                 'COTA_LOCAL/ELEVATION(m)']]

                    print('Planilha {} feita.'.format(item))

                    #salvando em diferentes DFs
                    df_1.to_csv('instrumentos/df_{}.csv'.format(item), index = False, encoding = 'utf-8')
                except:
                    pass
            #loop para concatenar os arquivos
            path_sc = 'instrumentos'

            files = glob.glob(path_sc + "/*.csv") #pegando os arquivos com o seu path

            filename = [] #criando lista vazia

            #criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)

            #lista vazia
            frames = []

            #criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:
                print('Concatenando {}'.format(arquivo))
                #lendo o arquivo
                df2 = pd.read_csv(arquivo)

                 #appending
                frames.append(df2)
            #concatenando todos os arquivos
            df = pd.concat(frames, axis=0, ignore_index = True)

            shape_info = df.shape
            st.write(
                'Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(
                    shape_info[0],
                    shape_info[1],
                    len(frames),
                    (len(frames) / len(sheets)) * 100))
            # mostrando o df modificado
            df

            #salvando o aquivo em apenas um
            df.to_csv('tabela_pze_concatenada.csv', index = False )

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_PZE_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)

    #opção para processar os dados de INAs
    if option == 'INAs':
        if uploaded_file is None:
            print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:
            print(st.markdown('''
                                     ▶️ Iniciando o processamento dos dados de INA...\n
                                       ▶️ Isso pode levar alguns instantes!
                                  '''))

            df = pd.read_excel(uploaded_file, sheet_name=None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names
            deletando_pasta('inas')
            for index, item in enumerate(sheets):
                try:
                    # fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    # colocando as coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    # aplicando o cabecalho

                      # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]
                    y = x[1] + 1


                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass

                    # remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)

                    # criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte

                    # reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO', 'Data',
                                 'NORTE', 'LESTE',
                                 'MCA/WATER LEVEL(m)',
                                 'COTA_LOCAL/ELEVATION(m)',
                                 'LEITURA_SENSOR/DEPTH(m)']]

                    # formatando a coluna de data
                    df_1['Data'] = pd.to_datetime(df_1['Data'], errors='coerce')

                    #forçando que as colunas que devem ser float fiquem com NaN enquanto for str
                    cols = ['MCA/WATER LEVEL(m)', 'LEITURA_SENSOR/DEPTH(m)', 'COTA_LOCAL/ELEVATION(m)']
                    mask = df_1[cols].applymap(lambda x: isinstance(x, (int, float)))

                    df_1[cols] = df_1[cols].where(mask)

                    print('Planilha {} feita.'.format(item))

                    # fazer o apêndice de cada df numa df maior.
                    # df_mrn.append(df_1)

                    # salvando em diferentes DFs
                    df_1.to_csv('inas/df_{}.csv'.format(item), index=False, encoding='utf-8')
                except:
                    pass

            st.write('As planilhas já foram organizadas:')

            path_sc = 'inas'

            files = glob.glob(path_sc + "/*.csv")  # pegando os arquivos com o seu path

            filename = []  # criando lista vazia
            # criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)
            # lista vazia
            frames = []

            # criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:
                # lendo o arquivo
                df2 = pd.read_csv(arquivo)
                # appending
                frames.append(df2)

            shape_info = df.shape
            st.write(
                'Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(
                    shape_info[0],
                    shape_info[1],
                    len(frames),
                    (len(frames) / len(sheets)) * 100))

            # mostrando o df modificado
            df
            # salvando o aquivo em apenas um
            df.to_csv('tabela_inas_concatenada.csv', index=False)

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_INA_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)
            
    #opção para processar os dados de NRs
    if option == 'NR':
        if uploaded_file is None:
            print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:
            print(st.markdown('''
                                     ▶️ Iniciando o processamento dos dados de NR...\n
                                       ▶️ Isso pode levar alguns instantes!
                                  '''))
            df = pd.read_excel(uploaded_file, sheet_name=None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names
            deletando_pasta('nr')

            for index, item in enumerate(sheets):
                try:
                    # fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    # colocando as coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    # aplicando o cabecalho

                    #  # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]
                    y = x[1] + 1

                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass


                    # remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)

                    # criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte

                    # reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO',
                                 'Data',
                                 'NORTE',
                                 'LESTE',
                                 'COTA_LOCAL/ELEVATION(m)']]

                    # formatando a coluna de data
                    df_1['Data'] = pd.to_datetime(df_1['Data'], errors='coerce')

                    print('Planilha {} feita.'.format(item))

                    # fazer o apêndice de cada df numa df maior.
                    # df_mrn.append(df_1)

                    # salvando em diferentes DFs
                    df_1.to_csv('nr/df_{}.csv'.format(item), index=False, encoding='utf-8')
                except:
                    pass
            path_sc = 'nr'

            files = glob.glob(path_sc + "/*.csv")  # pegando os arquivos com o seu path

            filename = []  # criando lista vazia

            # criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)

            # lista vazia
            frames = []

            # criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:
                print('Concatenando {}'.format(arquivo))
                # lendo o arquivo
                df2 = pd.read_csv(arquivo)

                # appending
                frames.append(df2)
            # concatenando todos os arquivos
            df = pd.concat(frames, axis=0, ignore_index=True)

            shape_info = df.shape
            st.write(
                'Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(
                    shape_info[0],
                    shape_info[1],
                    len(frames),
                    (len(frames) / len(sheets)) * 100))

            # mostrando o df modificado
            df

            # salvando o aquivo em apenas um
            df.to_csv('tabela_nr_concatenada.csv', index=False)

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_NR_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)

    #opção para processar dados de MNAs
    if option == 'MNA':
        if uploaded_file is None:
            print(st.markdown(''' ❌ Por favor, insira um arquivo de até 200MB!'''))

        if uploaded_file is not None:
            print(st.markdown('''
                                     ▶️ Iniciando o processamento dos dados de MNA...\n
                                       ▶️ Isso pode levar alguns instantes!
                                  '''))
            df = pd.read_excel(uploaded_file, sheet_name=None)
            xlsx = pd.ExcelFile(uploaded_file)

            sheets = xlsx.sheet_names
            deletando_pasta('mna')
            for index, item in enumerate(sheets):
                try:
                    # fazendo um dataframe para cada aba presente na planilha
                    df_1 = df[sheets[index]]

                    # colocando as coordenadas em variáveis
                    leste = df_1['Unnamed: 2'][8]
                    norte = df_1['Unnamed: 2'][9]

                    # aplicando o cabecalho

                     # primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                    # como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                    x = df_1[df_1['Unnamed: 1'].isin(['Data',
                                                      'DATA E HORA\n(UTC-03:00) Brasilia']
                                                    )].index.to_list()

                    # em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                    # valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                    df_1.columns = df_1.iloc[x[1]]
                    y = x[1] + 1

                    # removendo as 42 colunas acima que não são necessárias
                    df_1.drop(index=df_1.index[:y], axis=0, inplace=True)

                    # forçando o renome da coluna de data e hora paara apenas "data" caso seja diferente
                    if df_1.columns[1] == 'DATA E HORA\n(UTC-03:00) Brasilia':
                        df_1.rename(columns = {'DATA E HORA\n(UTC-03:00) Brasilia' : 'Data'}, inplace = True)
                    else:
                        pass

                    # remover a primeira coluna vazia e também outras possíveis colunas
                    df_1.dropna(how='all', axis=1, inplace=True)

                    # criando uma coluna com o nome do instrumento
                    df_1['INSTRUMENTO'] = item
                    df_1['LESTE'] = leste
                    df_1['NORTE'] = norte

                    # reorganizando as colunas
                    df_1 = df_1[['INSTRUMENTO',
                                'Data',
                                 'NORTE',
                                 'LESTE',
                                 'COTA_LOCAL/ELEVATION(m)',
                                 'LEITURA_SENSOR/DEPTH(m)',
                                 'MCA/WATER LEVEL(m)']]

                    # formatando a coluna de data
                    df_1['Data'] = pd.to_datetime(df_1['Data'], errors='coerce')

                    # forçando que as colunas que devem ser float fiquem com NaN enquanto for str
                    cols = ['MCA/WATER LEVEL(m)', 'LEITURA_SENSOR/DEPTH(m)', 'COTA_LOCAL/ELEVATION(m)']
                    mask = df_1[cols].applymap(lambda x: isinstance(x, (int, float)))

                    df_1[cols] = df_1[cols].where(mask)

                    print('Planilha {} feita.'.format(item))

                    # fazer o apêndice de cada df numa df maior.
                    # df_mrn.append(df_1)

                    # salvando em diferentes DFs
                    df_1.to_csv('mna/df_{}.csv'.format(item), index=False, encoding='utf-8')
                except:
                    pass
            path_sc = 'mna'

            files = glob.glob(path_sc + "/*.csv")  # pegando os arquivos com o seu path

            filename = []  # criando lista vazia

            # criando loop para criar uma lista com todos os paths dos arquivos
            for file in files:
                file_List = (file)
                filename.append(file_List)

            # lista vazia
            frames = []

            # criando loop para concatenar todos os arquivos dentro de filename
            for arquivo in filename:
                print('Concatenando {}'.format(arquivo))
                # lendo o arquivo
                df2 = pd.read_csv(arquivo)

                # appending
                frames.append(df2)
            # concatenando todos os arquivos
            df = pd.concat(frames, axis=0, ignore_index=True)

            shape_info = df.shape
            st.write(
                'Sua planilha tem {} linhas e {} colunas. No total, {} abas foram concatenadas. Uma taxa de sucesso de {:.2f}%'.format(
                    shape_info[0],
                    shape_info[1],
                    len(frames),
                    (len(frames) / len(sheets)) * 100))

            # mostrando o df modificado
            df

            # salvando o aquivo em apenas um
            df.to_csv('tabela_mna_concatenada.csv', index=False)

            towrite = io.BytesIO()
            downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
            towrite.seek(0)  # reset pointer
            b64 = base64.b64encode(towrite.read()).decode()  # some strings
            linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_MNA_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
            st.markdown(linko, unsafe_allow_html=True)

#Configurando barra lateral

#colocando a imagem
st.sidebar.image('MDGEO.jpeg', width = 250)

#título do sobre o app
st.sidebar.title('Sobre o app')
st.sidebar.markdown('''
O app tem objetivo tonar o processamento e compilação de dados mais veloz, 
fazendo com que foquemos no que realmente importa: **analisar os dados**.''')

#título do manual
st.sidebar.title('Manual')
st.sidebar.markdown('''
Para garantir o uso ideal do app, evitando o _funcionamento indesejado_, por gentileza, [leia o manual](https://github.com/rodreras/conversor_app/blob/main/readme.md)
''')

#título do suporte  
st.sidebar.title('Suporte')
st.sidebar.markdown(''' 
                    Em caso de bugs ou sugestões de melhorias, por favor, entre em contato pelo e-mail
[rodrigo.brusts@mdgeomam.com.br](https://github.com/rodreras/conversor_app#suporte).
                    ''')
                    
#título sobre o código
st.sidebar.title("Código")
st.sidebar.markdown("[![Github Badge] (https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white&link=https://github.com/rodreras)](https://github.com/rodreras/conversor_app)")
st.sidebar.markdown(''' _Versão: 0.4_''')
st.sidebar.markdown('''01/09/2021_ ''')
