import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time
import streamlit as st
import traceback
import os
import glob
import base64
import io 


st.set_page_config(page_title = 'MDGeo Converter')
logo = 'mdgeo.png'
#Título e Subtítulo


col1, col2 = st.beta_columns([1,8])

col2.header('MDGeo Apps')
col1.image(logo, width = 90)
 
 

#st.image(logo)
#st.title('MDGeo Apps')

st.header('Conversor de Dados do SHMS')






st.markdown('''
Aplicação desenvolvida pelo Setor de Modelagem da MDGeo com intuito de
facilitar o processamento dos dados da plataforma SHMS. Ao inserir os dados, 
o app irá concatenar todas as abas da planilha de Excel em apenas uma, facilitando
assim processamentos posteriores.


 ''')
 
option = st.radio('O arquivo está no formato XLSX?', ['Sim','Não'])

if option == 'Não':

    print(st.markdown('''
                     **Por favor, converta o arquivo para `XLSX` e
                     faça o upload.**
                  '''))

uploaded_file = st.file_uploader("Escolha um arquivo")

if option == 'Sim':

   
    
    if uploaded_file is not None:
            
        df =  pd.read_excel(uploaded_file, sheet_name = None)
        xlsx = pd.ExcelFile(uploaded_file)
        
        sheets = xlsx.sheet_names
        
        print(st.markdown('''
                     **Iniciando o processamento. Isso pode levar alguns instantes!**
                  '''))
        
        for index, item in enumerate(sheets):
            try:    
                #fazendo um dataframe para cada aba presente na planilha
                df_1 = df[sheets[index]]                   

                #aplicando o cabecalho

                #primeiro, buscando o valor data dentro da coluna 2 e colocando as ocorrencias numa lista
                #como há uma ocorrência de data antes, sempre escolheremos o índice 2.'''
                x = df_1[df_1['Unnamed: 1'] == 'Data'].index.to_list()

                #em seguida, dizemos que as colunas do df_1 nada mais é do que a linha da segunda ocorrência do
                #valor "data", uma vez que dependendo da aba, esse valor encontra-se em diferentes linhas'''
                df_1.columns = df_1.iloc[x[1]]

                 #removendo as 42 colunas acima que não são necessárias
                df_1.drop(index = df_1.index[:42], axis = 0, inplace = True)

                #remover a primeira coluna vazia e também outras possíveis colunas 
                df_1.dropna(how='all', axis=1, inplace=True)


                #criando uma coluna com o nome do instrumento
                df_1['INSTRUMENTO'] = item 

                #reorganizando as colunas
                df_1 = df_1[['INSTRUMENTO',
                             'Data',
                             'COTA/ELEVATION(m)',
                             'THERMISTOR/ELECTRICAL RESISTANCE(Ohm)',
                             'MCA/WATER LEVEL(m)',
                             'FREQUENCIA/FREQUENCY(Hz)',
                             'KPA/PRESSURE(kPA)',
                             'TEMPERATURA/TEMPERATURE(°C)',
                             'COTA_LOCAL/ELEVATION(m)']]

                print('Planilha {} feita.'.format(item))

                #fazer o apêndice de cada df numa df maior.
                #df_mrn.append(df_1)

                #salvando em diferentes DFs
                df_1.to_csv('instrumentos/df_{}.csv'.format(item), index = False, encoding = 'utf-8')
            except:
                #print('Erro na aba {}'.format(item)
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
        
        #salvando o aquivo em apenas um
        df.to_csv('tabela_concatenada.csv', index = False )
        
        towrite = io.BytesIO()
        downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
        towrite.seek(0)  # reset pointer
        b64 = base64.b64encode(towrite.read()).decode()  # some strings
        linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="SHMS_concatenado.xlsx">📂 Baixar Tabela Concatenada</a>'
        st.markdown(linko, unsafe_allow_html=True)


st.sidebar.title('Sobre o app')

st.sidebar.markdown('''
O app tem objetivo tonar o processamento e compilação de dados mais veloz, 
fazendo com que foquemos no que realmente importa: **analisar os dados**.

Em caso de bugs ou sugestões de melhorias, por favor, entre em contato pelo e-mail:
`rodrigo.brusts@mdgeomam.com.br`
''')


st.sidebar.title("Código")
st.sidebar.markdown("[![Github Badge] (https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white&link=https://github.com/rodreras)](https://github.com/rodreras/conversor_app)")
