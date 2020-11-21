# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 12:56:13 2020

@author: Jacques Pienaar 
jaypienaar.com

"""

import sys
import os
import pandas as pd
import numpy as np

def similar_names(a, b, threshold = 2):
    names1 = []
    names2 = []
    multimatch1 = set()
    multimatch2 = set()
    for name1 in a:
        for name2 in b:
            words1 = name1.lower().split()
            words2 = name2.lower().split()
            common = set(words1).intersection(words2)
            if (len(common) >= threshold and words1[0] == words2[0]):
                if name1 in names1:
                    multimatch1.add(name1)
                if name2 in names2:
                    multimatch2.add(name2)
                names1.append(name1)
                names2.append(name2)
    return names1, names2, multimatch1, multimatch2

def main():
    print('Olá! Você está usando combina.py, '
          'desenvolvido por Jacques Pienaar, \n'
          'uma programa simples para fundir '
          'tabelas de notas e provas, \nusando '
          'os nomes dos estudantes. \n'
          'A programa está começando...')
    # Get data from files:
    print('Procurando arquivos notas.csv e provas.csv ...', end='')
    try:
        filepath = os.getcwd()
        notas = pd.read_csv(filepath + '\\notas.csv', 
                            encoding='latin-1')
        provas = pd.read_csv(filepath + '\\provas.csv', 
                             encoding='latin-1')
    except FileNotFoundError:
        print('Erro: Não achei os arquivos notas.csv e provas.csv .'
              '\nPor favor verifique que os arquivos estão nomeado '
              'corretamente, e que eles ficam '
              'na pasta {}'.format(filepath))
        ending = input('(Digite qualquer tecla para sair.) ')
        sys.exit()
    print(' successo.')
    # Tidy up the data:
    print('Organizando os dados...', end='')
    provas = provas.dropna(axis=0,how='all')
    provas = provas.dropna(axis=1,how='all')
    provas.rename(columns={provas.columns[0]:'Nome', 
                           provas.columns[1]:'ID'},
                  inplace = True)
    provas.replace(['á','ã','é','ê','í','õ','ó','ô','ú','ç'],
                   ['a','a','e','e','i','o','o','o','u','c'],
                   regex=True,
                   inplace=True)


    notas = notas.dropna(axis=0,how='all')
    notas = notas.dropna(axis=1,how='all')
    notas.rename(columns={notas.columns[0]:'First name', 
                          notas.columns[1]:'Surname',
                          notas.columns[2]:'ID'},
                 inplace = True)
    notas.replace(['á','ã','é','ê','í','õ','ó','ô','ú','ç'],
                  ['a','a','e','e','i','o','o','o','u','c'],
                  regex=True,
                  inplace=True)

    notas = notas.assign(Nome = notas['First name']+' '+notas['Surname'] )
    notas = notas[['Nome']+list(notas.columns[2:-1])]
    
    # Check that no IDs are duplicated:
    notas_IDs = notas.dropna(subset=['ID'])
    provas_IDs = provas.dropna(subset=['ID'])
    try:
        assert len(notas_IDs['ID'].unique()) == len(notas_IDs)
        assert len(provas_IDs['ID'].unique()) == len(provas_IDs)
    except AssertionError:
        print('Erro: Algumas números de identificação estão '
              'repetidos. \nVerifique que cada número parece '
              'somente um vez em cada tabela, e tente de novo.')
        ending = input('(Digite qualquer tecla para sair.) ')
        sys.exit()

    # If a name has duplicates in one of the lists, ensure
    # all instances of it in that list are accompanied by IDs:

    n_count = notas.Nome.value_counts()
    n_multi = n_count[n_count >1]
    # TODO: rewrite using try/except
    for n in n_multi:
        problem = len(notas[(notas.Nome == n)&(notas['ID'].isna())])
        if problem:
            print('Erro: o nome {} parece multiplus vezes no arquivo "notas". '
                     '\nPor favor '
                     'coloque números de identificação distintos para eles '
                     'e tente de novo.'.format(n))
            ending = input('(Digite qualquer tecla para sair.) ')
            sys.exit()
        
    p_count = provas.Nome.value_counts()
    p_multi = p_count[p_count >1]        
    for p in p_multi:
        problem = len(provas[(provas.Nome == p)&(provas['ID'].isna())])
        if problem:
            print('Erro: o nome {} parece multiplus vezes no arquivo "provas". '
                     '\nPor favor '
                     'coloque números de identificação distintos para eles '
                     'e tente de novo.'.format(n))
            ending = input('(Digite qualquer tecla para sair.) ')
            sys.exit()
    print(' successo.')
    # Assign unique IDs (UIDs) based on common IDs:
    print('Comparando os nomes dos estudantes ...')
    common_ID = pd.merge(notas_IDs, provas_IDs, how='inner', on='ID',
                         suffixes=('_n','_p')) 
    UID = 0
    notas = notas.assign(UID = np.nan)
    provas = provas.assign(UID = np.nan)
    for i in common_ID.ID:
        notas.loc[notas.ID == i,'UID'] = UID
        provas.loc[provas.ID == i, 'UID'] = UID
        UID += 1
        
    # Assign UIDs based on similar names:
    notas = notas.assign(nameid = notas.Nome)
    notas.ID = notas.ID.apply(str)
    notas.loc[notas.ID == 'nan', 'ID'] = 'desconhecido'
    notas.nameid += ' (ID:--' + notas.ID + ')'

    provas = provas.assign(nameid = provas.Nome)
    provas.ID = provas.ID.apply(str)
    provas.loc[provas.ID == 'nan', 'ID'] = 'desconhecido'
    provas.nameid += ' (ID:--' + provas.ID + ')'

    # Get name lists excluding those which already have a UID
    n_names = notas.nameid[notas.UID.isna()].to_list()
    p_names = provas.nameid[provas.UID.isna()].to_list()

    [n,p,n_multi,p_multi] = similar_names(n_names,p_names)

    pairs = pd.DataFrame({'n': [n[i] for i in range(len(n))],
                          'p': [p[i] for i in range(len(p))]})

    # Get user to resolve ambiguous matches:
    # For each name in the n column with multiple matches, 
    # ask the user which of its several matches from the 
    # p column is the correct match.
    # Remove the false matches. Then repeat the process
    # for the p column.
    # TODO: Exclude matches with incompatible IDs
    # TODO: Give an option to say "Não sei".

    for n in n_multi:
        matches = pairs.p[pairs.n == n].to_list()
        num_options = len(matches)+1
        print('Me ajuda, por favor. O nome {} no arquivo notas.csv \n'
              'corresponde com qual das seguintes pessoas'
              'no arquivo provas.csv? \nEscolhe um:'.format(n))
        for i in range(len(matches)):
            print('({}) {} '.format(i+1,matches[i]) )
        print('({}) Nenhuma deles acima.'.format(num_options))
        ans = False
        while not ans:
            ans = int(input('Insira o número correspondente '
                            'à sua resposta: '))
            if ans not in range(1,num_options+1):
                print('Por favor, insira um númer entre '
                      '1 e {}.'.format(len(matches)+1))
                ans = False
        if ans == num_options:
            pairs = pairs[pairs.n != n]  
        else:
            p = matches[ans-1]
            pairs = pairs[((pairs.n != n) & (pairs.p != p))     
                          | ((pairs.n == n) & (pairs.p == p))]  

# Repeat for any remaining ambiguous matches in the p column:

    for p in p_multi:
        matches = pairs.n[pairs.p == p].to_list()
        num_options = len(matches)+1
        print('Me ajuda, por favor. O nome {} no arquivo notas.csv \n'
              'corresponde com qual das seguintes pessoas'
              'no arquivo provas.csv? \nEscolhe um:'.format(p))
        for i in range(len(matches)):
            print('({}) {} '.format(i+1,matches[i]) )
        print('({}) Nenhuma deles acima.'.format(num_options))
        ans = False
        while not ans:
            ans = input('Insira o número correspondente à '
                        'sua resposta: ')
            try:
                ans = int(ans)
                assert(ans in range(1,num_options+1))
            except:
                print('Por favor, insira um númer entre '
                      '1 e {}.'.format(len(matches)+1))
                ans = False
        if ans == num_options:
            pairs = pairs[pairs.p != p] 
        else:
            n = matches[ans-1]
            pairs = pairs[((pairs.n != n) & (pairs.p != p))     
                          | ((pairs.n == n) & (pairs.p == p))]  
                  
    # Assign unique UIDs to the matches found
        
    for n in pairs.n:
        for p in pairs.p[pairs.n == n]:
            notas.loc[notas.nameid == n, 'UID'] = UID
            provas.loc[provas.nameid == p, 'UID'] = UID
            UID += 1
            
    # ...and give unique UIDs to the remaining students:
        
    x = notas.UID[notas.UID.isna()]
    UIDs = [UID+i for i in range(len(x))]
    notas.loc[notas.UID.isna(), 'UID'] = UIDs
    UID += len(x)
    
    y = provas.UID[provas.UID.isna()]
    UIDs = [UID+i for i in range(len(y))]
    provas.loc[provas.UID.isna(), 'UID'] = UIDs
    UID += len(y) 

    # Combine the data:
    print('Obrigado! Estou fundindo as tabelas...', end='')
    # Restore the IDs
    notas.loc[notas.ID == 'desconhecido', 'ID'] = np.nan
    provas.loc[provas.ID == 'desconhecido', 'ID'] = np.nan

    # Fill in any missing ID numbers:
    
    u_ids = {}
    for u in range(UID):
        ids = (notas.ID[notas.UID == u].dropna().tolist() + 
               provas.ID[provas.UID == u].dropna().tolist() )
        if ids:
            u_ids[u] = ids[0] 
        else:
            u_ids[u] = np.nan
    
    for u in range(UID):
        notas.loc[notas.UID == u, 'ID'] = u_ids[u]
        provas.loc[provas.UID == u, 'ID'] = u_ids[u]

    # Make final merged table
        
    # Drop unnecessary columns
    notas.drop(columns=['nameid'], inplace=True)
    provas.drop(columns=['nameid'], inplace=True)

    # Merge 
    final = pd.merge(notas, provas, 
                     how='outer', on=['UID','ID'], suffixes=('_1','_2'))

    # Tidy up columns
    upfront_cols = ['Nome_1','Nome_2','ID']
    new_columns = upfront_cols + final.columns.drop(upfront_cols+['UID']).tolist()
    final = final[new_columns]
    
    # save to output file
    print(' successo. \nSalvando o arquivo...', end='')
    final.to_csv(filepath + '\\combined.csv', na_rep = '#N/A', encoding='latin-1')
    print(' successo.')
    print('Pode achar o novo tabela no '
          'arquivo {}\\combined.csv . \n'
          'A programa está terminado. Obrigado.'.format(filepath))
    ending = input('(Digite qualquer tecla para sair.) ')
    sys.exit()

if __name__ == '__main__':
  main()