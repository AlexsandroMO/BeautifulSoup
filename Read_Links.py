!pip install bs4
!pip install xlsxwriter

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
import xlsxwriter

link_1 = 'https://www.angra.rj.gov.br/licitacoes-procedimentos.asp?indexsigla=transp&cd_opcao=0&cd_modal=0&cd_statu=0&cd_pesqu=&cd_ano=2022'
link_2 = 'https://www.eletronuclear.gov.br/Canais-de-Negocios/Licitacoes/Paginas/Licitacoes.aspx'
link_3 = 'https://www.in.gov.br/leiturajornal?data=25-08-2020&secao=DO3'
link_4 = 'https://www.pciconcursos.com.br/'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}

response_object1 = requests.get(link_1, headers=headers)
response_object3 = requests.get(link_3, headers=headers)

search_soup1 = BeautifulSoup(response_object1.text, features='html.parser')
search_soup3 = BeautifulSoup(response_object3.text, features='html.parser')

#---------------------------
#Search: https://www.in.gov.br/leiturajornal?data=25-08-2020&secao=DO3
gov_elemt = search_soup3.find(id='params')

#----------------------------
table_list = []
for a in gov_elemt:
  data = json.loads(a)
  for b in data['jsonArray']:
    table_list.append([b['title'],b['content'], b['title'], b['hierarchyList'], b['urlTitle'],b['pubDate']])

df_lista_gov = pd.DataFrame(data=table_list,columns=['EDITAL','TEXTO_NOTIFICA','X','LOCAIS','LINK','DATA'])
df_lista_gov.drop(columns=['X'], inplace=True)

for a in range(0, len(df_lista_gov['LINK'][0])):
  df_lista_gov['LINK'].loc[a] = 'https://www.in.gov.br/web/dou/-/' + df_lista_gov['LINK'].loc[a]

writer = pd.ExcelWriter('LINKS_JOIN.xlsx', engine='xlsxwriter')
df_lista_gov.to_excel(writer, sheet_name='LISTA_IN_GOV')
#writer.save()

#---------------------------
#Search: https://www.angra.rj.gov.br/licitacoes-procedimentos.asp?indexsigla=transp&cd_opcao=0&cd_modal=0&cd_statu=0&cd_pesqu=&cd_ano=2022
licit_elemt1 = search_soup1.select('div')
arq_elemt1 = search_soup1.find_all('a')

#---------------------- LICIT
path_read = []
for a in licit_elemt1:
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
    lido = df['LICIT'].loc[cont]

df_lista  = pd.DataFrame(data=new_df, columns=['LICIT','DATA','OBJETIVO','SECRETARIA'])

#---------------------- ARQ
LINK_LICIT = []
for a in range(0, len(df['LICIT'])):
  search_link = df['LICIT'].loc[a].replace('/','-')
  for b in arq_elemt1:
    m = re.search('(?<=' + search_link + ').*', str(b.get('href')))
    if m != None:
      LINK_LICIT.append([df['LICIT'].loc[a], b.get('href')])

df_link = pd.DataFrame(data=LINK_LICIT, columns=['LICIT','LINK'])

for a in range(0, len(df_link['LINK'])):
  df_link['LINK'].loc[a] = 'https://www.angra.rj.gov.br/' + df_link['LINK'].loc[a]

#writer = pd.ExcelWriter('LINKS_JOIN.xlsx.xlsx', engine='xlsxwriter')
df_lista.to_excel(writer, sheet_name='PREF_ANGRA_LICITA')
df_link.to_excel(writer, sheet_name='PREF_ANGRA_LINK')
writer.save()
