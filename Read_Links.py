!pip install xlsxwriter

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import xlsxwriter

link_1 = 'https://www.angra.rj.gov.br/licitacoes-procedimentos.asp?indexsigla=transp&cd_opcao=0&cd_modal=0&cd_statu=0&cd_pesqu=&cd_ano=2022'
link_2 = 'https://www.eletronuclear.gov.br/Canais-de-Negocios/Licitacoes/Paginas/Licitacoes.aspx'
link_3 = 'https://www.in.gov.br/leiturajornal?data=25-08-2020&secao=DO3'
link_4 = 'https://www.pciconcursos.com.br/'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}
response_object = requests.get(link_1, headers=headers)

search_soup = BeautifulSoup(response_object.text, features='html.parser')

test_elemt = search_soup.select('div')
arq_elemt = search_soup.find_all('a')

path_read = []
for a in test_elemt:
  path_read.append(a.text.replace('\r','').replace('\t',''))

treat_all = []
for a in path_read:
  result = a.split('\n')
  for i in result:
    if i != '':
      if i != '      ':
        if i != '          ':
          treat_all.append(i)

read_all = []
a,b,c,d = '','','',''
for cont in range(0, len(treat_all)):
  if treat_all[cont][:13] == 'Licitação Nº:':
    a = treat_all[cont+1]
  if treat_all[cont][:6] == ' Data:':
    b = treat_all[cont+1]
  if treat_all[cont][:7] == 'Objeto:':
    c = treat_all[cont]
  if treat_all[cont][:11] == 'Secretaria:':
    d = treat_all[cont]

  read_all.append([a,b,c,d])

ajust = []
for x in read_all:
  if len(x) == 4:
    ajust.append(x)

df = pd.DataFrame(data=ajust, columns=['LICIT','DATA','OBJETIVO','SECRETARIA'])
df = df[(df['LICIT'] != '') & (df['DATA'] != '') & (df['OBJETIVO'] != '') & (df['SECRETARIA'] != '')]
df = df.drop_duplicates (subset = None, keep = 'last', inplace = False)
df.reset_index(inplace=True, drop=False)

new_df = []
new_df.append([df['LICIT'].loc[0],df['DATA'].loc[0],df['OBJETIVO'].loc[0],df['SECRETARIA'].loc[0]])
lido = '025/2022'
for cont in range(0, len(df['LICIT'])):
  if df['LICIT'].loc[cont] != lido:
    new_df.append([df['LICIT'].loc[cont],df['DATA'].loc[cont],df['OBJETIVO'].loc[cont],df['SECRETARIA'].loc[cont]])
    #print(cont, df['LICIT'].loc[cont])
    lido = df['LICIT'].loc[cont]

df_lista  = pd.DataFrame(data=new_df, columns=['LICIT','DATA','OBJETIVO','SECRETARIA'])

LINK_LICIT = []
for a in range(0, len(df['LICIT'])):
  search_link = df['LICIT'].loc[a].replace('/','-')
  #print(search_link.replace('/','-'))
  for b in arq_elemt:
    m = re.search('(?<=' + search_link + ').*', str(b.get('href')))
    if m != None:
      LINK_LICIT.append([df['LICIT'].loc[a], b.get('href')])

df_link = pd.DataFrame(data=LINK_LICIT, columns=['LICIT','LINK'])

writer = pd.ExcelWriter('LISTA_LITIC.xlsx', engine='xlsxwriter')

df_lista.to_excel(writer, sheet_name='LICITA')
df_link.to_excel(writer, sheet_name='LINK')

writer.save()
