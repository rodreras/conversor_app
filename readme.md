# Manual do Usuário - MDGeo SHSMS Converter
_______________

<a id='app'></a>
## [Sobre o App](#app)

Este aplicativo foi desenvolvido pelo setor de Modelagem da MDGeo com o objetivo de facilitar o tratamento dos dados coletados no sistema SHMS. Dessa forma, é possível filtrar e concatenar dezenas, ou até mesmo centenas de colunas em apenas uma única planilha. 

Para seu funcionamento ideal, recomenda-se a leitura da tópico abaixo [Como Usar](#uso), garantindo assim o mínimo de bug. Porém, ainda que você siga todos os passos corretamente e mesmo assim apresente erros, siga os passos do [Suporte](#sup)

<a id='uso'></a>
## [Como Usar](#uso)

#### I) Selecionando o Tipo de Instrumento

O primeiro passo para que possamos converter os documentos, é escolher o tipo de equipamento. Para que a 
conversão seja eficiente, é preciso garantir que as colunas estejam iguais aos modelos abaixo.

`1.` Dados de PZE


|Data|COTA/ELEVATION(m)|THERMISTOR/ELECTRICAL RESISTANCE(Ohm)|MCA/WATER LEVEL(m)|FREQUENCIA/FREQUENCY(Hz)|KPA/PRESSURE(kPA)|TEMPERATURA/TEMPERATURE(°C)|COTA_LOCAL/ELEVATION(m)|
|----|-----------------|-------------------------------------|------------------|------------------------|-----------------|---------------------------|-----------------------|


`2.` Dados de PZC

|Data|LEITURA_SENSOR/DEPTH(m)|COTA_LOCAL/ELEVATION(m)|MCA/WATER LEVEL(m)|
|----|-----------------------|-----------------------|------------------|

`3.` Dados de NR

|Data|COTA_LOCAL/ELEVATION(m)|
|----|-----------------------|

`4.` Dados de INA

|Data|MCA/WATER LEVEL(m)|COTA_LOCAL/ELEVATION(m)|LEITURA_SENSOR/DEPTH(m)|
|----|-----------------------|-----------------------|------------------|

`5.` Dados de MNA

|Data|LEITURA_SENSOR/DEPTH(m)|COTA_LOCAL/ELEVATION(m)|MCA/WATER LEVEL(m)|
|----|-----------------------|-----------------------|------------------|

#### II) Escolher o Tipo de Filtro

Para facilitar a visualização e manipulação dos dados, existem duas opções de filtros: 

- `Filtrados`: permite que você selecione datas para filtrar seus dados, e gere uma planilha concatenada filtrada.

- `Completos`: ao contrário da outra opção, apenas concatena os seus dados em uma única planilha.

#### III) Inserir Arquivo

Por fim, para poder gerar o resultado final, você deve colocar o arquivo com extensão `xlsx`. Uma vez que o arquivo
for carregado, o processamento iniciará.

#### IV) Resultados

- Indicador de sucesso: a porcentagem indica quantas planilhas do total foram convertidas com sucesso.

- Tabela de pré-visualização da conversão.

- Link para baixar a tabela.


<a id='sup'></a>
## [Suporte](#sup)

Em caso de bugs ou sugestões de melhorias, por favor, entre em contato pelo e-mail
**`rodrigo.brusts@mdgeomam.com.br`**, de acordo com cada tópico específico:

#### Para bugs, coloque o assunto do e-mail como `Suporte App SHMS - Bug`

**Siga esses passos**

1 - Descreva o que aconteceu

2 - Descreva o que você esperava

3 - Envie prints dos erros

4 - Envie prints da planilha que você inseriu


**Perguntas para responder antes de enviar um email**

- A planilha estava de acordo com o modelo ideal, apontado em [Como Usar](#uso)?
	
- Você selecionou a opção do instrumento corretamente? 

#### Para sugestões, coloque o assunto do e-mail como `Suporte App SHMS - Sugestões`

1 - Explique o que deseja.

2 - Explique se é uma tarefa manual feita com frequência.

3 - Se possível, mostre os dados antes e após o processamento desejado com prints.

4 - Explique se os dados são padronizados ou não.

<a id='dev'></a>
## Desenvolvimento

**Setor de Modelagem Numérica**

Responsável: Julio Yasbek

Desenvolvimento: Rodrigo Brust

<a id='ver'></a>
## Versão

Versão: `0.1`
Update: `2021-07-28`

