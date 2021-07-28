# Manual do Usuário - MDGeo SHSMS Converter
_______________

<a id='app'></a>
## [Sobre o App](#app)

Este aplicativo foi desenvolvido pelo setor de Modelagem da MDGeo com o objetivo de facilitar o tratamento dos dados coletados no sistema SHMS. Dessa forma, é possível filtrar e concatenar dezenas, ou até mesmo centenas de colunas em apenas uma única planilha. 

Para seu funcionamento ideal, recomenda-se a leitura da tópico abaixo [Como Usar](#uso), garantindo assim o mínimo de bug. Porém, ainda que você siga todos os passos corretamente e mesmo assim apresente erros, siga os passos do [Suporte](#sup)

<a id='uso'></a>
## [Como Usar](#uso)

`1.` Dados de PZE

- `a)` Primeiro passo é coletar os dados na plataforma SHMS iguais as da tabela abaixo:

|Data|COTA/ELEVATION(m)|THERMISTOR/ELECTRICAL RESISTANCE(Ohm)|MCA/WATER LEVEL(m)|FREQUENCIA/FREQUENCY(Hz)|KPA/PRESSURE(kPA)|TEMPERATURA/TEMPERATURE(°C)|COTA_LOCAL/ELEVATION(m)|
|----|-----------------|-------------------------------------|------------------|------------------------|-----------------|---------------------------|-----------------------|


`2.` Dados de PZC

- `a)` Primeiro de tudo, para converter os dados de PZC, é preciso selecionar na plataforma SHMS as seguintes colunas:

|Data|LEITURA_SENSOR/DEPTH(m)|COTA_LOCAL/ELEVATION(m)|MCA/WATER LEVEL(m)|
|----|-----------------------|-----------------------|------------------|

Caso essas colunas não sejam respeitadas, muito provavelmente os dados não vão concatenar da forma correta.


`3.` Dados de NR

`Ferramenta ainda em desenvolvimento`

`4.` Dados de INA

`Ferramenta ainda em desenvolvimento`

`5.` Dados de MNA

`Ferramenta ainda em desenvolvimento`

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

