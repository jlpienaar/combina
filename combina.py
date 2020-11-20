# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 12:56:13 2020

@author: Jacques Pienaar 
jaypienaar.com

"""
import pandas as pd
import numpy as np
import sys
import os

# Given two CSV files, notas.csv and provas.csv, 
# containing students' names and marks,
# combine into a single table.
# Assumptions:
# notas includes columns for the first name, surname, ID, 
# and various marks columns.
# provas includes columns for the full name, ID, 
# and various marks columns.
# Strategy: 
# The goal is to create two tables that can be outer-joined on the basis
# of a number UID that uniquely identifies as many students as possible
# using their ID and name.
# To do this, we need to identify as many unique people as possible across the
# two lists, and give each unique person the same UID on each list.
# Match people in two stages. Stage 1: match by ID.
# Stage 2: match by name, with the user's help to resolve ambiguities.
# Finally, outer-join the tables on the UIDs, and drop the UID column.

# BUGS: Not associating Harry von whoami
#%% FIND THE FILES TO COMBINE:

os.chdir('C:\\Users\\jacques.pienaar\\Desktop\\Gabi notas\\combina')
filepath = os.getcwd()

notas = pd.read_csv(filepath + '\\notas-t3-test.csv', encoding='latin-1')

provas = pd.read_csv(filepath + '\\provas-t3-test.csv', encoding='latin-1')

#%% TIDY UP:

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
notas = notas[['Nome']+list(notas.columns[2:-1])]    # Can this be improved?


#%% FIX DUPLICATES IN EACH LIST
    
# Check that no IDs are duplicated:
notas_IDs = notas.dropna(subset=['ID'])
provas_IDs = provas.dropna(subset=['ID'])
assert len(notas_IDs['ID'].unique()) == len(notas_IDs)
assert len(provas_IDs['ID'].unique()) == len(provas_IDs)


# Make sure that if a name has duplicates in one of the lists, then
# all instances of it in that list must be accompanied by IDs.

n_count = notas.Nome.value_counts()
n_multi = n_count[n_count >1]
for n in n_multi:
    problem = len(notas[(notas.Nome == n)&(notas['ID'].isna())])
    if problem:
        sys.exit('Erro: o nome {} parece multiplus vezes no arquivo "notas". '
                 'Por favor '
                 'coloque números de identificação distintos para eles '
                 'e tente de novo.'.format(n))
        
p_count = provas.Nome.value_counts()
p_multi = p_count[p_count >1]        
for p in p_multi:
    problem = len(provas[(provas.Nome == n)&(provas['ID'].isna())])
    if problem:
        sys.exit('Erro: o nome {} parece multiplus vezes no arquivo "provas". '
                 'Por favor '
                 'coloque números de identificação distintos para eles '
                 'e tente de novo.'.format(n))

#%% ASSIGN UIDs BASED ON common ID

common_ID = pd.merge(notas_IDs, provas_IDs, how='inner', on='ID',
                     suffixes=('_n','_p')) 

UID = 0
notas = notas.assign(UID = np.nan)
provas = provas.assign(UID = np.nan)
for i in common_ID.ID:
    notas.UID[notas.ID == i] = UID
    provas.UID[provas.ID == i] = UID
    UID += 1
#%% DEFINE NAME MATCHING FUNCTION:

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

#%% ASSIGN UIDs BASED ON SIMILAR NAMES

# For the purposes of matching, 
# make a column that combines the ID numbers as part of the name.
# Note: This could be much more elegant... why not keep the IDs separate?

notas = notas.assign(nameid = notas.Nome)
notas.ID = notas.ID.apply(str)
notas.ID[notas.ID == 'nan'] = 'desconhecido'
notas.nameid += ' (ID: ' + notas.ID + ')'

provas = provas.assign(nameid = provas.Nome)
provas.ID = provas.ID.apply(str)
provas.ID[provas.ID == 'nan'] = 'desconhecido'
provas.nameid += ' (ID: ' + provas.ID + ')'

# Get name lists excluding those which already have a UID
n_names = notas.nameid[notas.UID.isna()].to_list()
p_names = provas.nameid[provas.UID.isna()].to_list()

[n,p,n_multi,p_multi] = similar_names(n_names,p_names)

pairs = pd.DataFrame({'n': [n[i] for i in range(len(n))],
                     'p': [p[i] for i in range(len(p))]})

#%% Get user to resolve ambiguous matches:

# For each name in the n column with multiple matches, ask the user 
# which of its several matches from the p column is the correct match.
# Remove the false matches. Then repeat the process for the p column.

for n in n_multi:
    matches = pairs.p[pairs.n == n].to_list()
    num_options = len(matches)+1
    print('O nome {} corresponde com qual das'
          ' seguintes pessoas?'.format(n))
    for i in range(len(matches)):
        print('({}) {} '.format(i+1,matches[i]) )
    print('({}) Nenhuma deles acima.'.format(num_options))
    ans = False
    while not ans:
        ans = int(input('Insira o número correspondente à sua resposta: '))
        if ans not in range(1,num_options+1):
            print('Por favor, insira um númer entre '
                  '1 e {}.'.format(len(matches)+1))
            ans = False
    print('ans = {}, num_opts = {}'.format(ans,num_options))
    if ans == num_options:
        pairs = pairs[pairs.n != n]  # Drop all matches with that name.
    else:
        print('else statement activated')
        p = matches[ans-1]
        pairs = pairs[((pairs.n != n) & (pairs.p != p))     # Drop all except
                      | ((pairs.n == n) & (pairs.p == p))]  # the correct pair.

# Repeat for any remaining ambiguous matches in the p column:

for p in p_multi:
    matches = pairs.n[pairs.p == p].to_list()
    num_options = len(matches)+1
    print('O nome {} corresponde com qual das'
          ' seguintes pessoas?'.format(p))
    for i in range(len(matches)):
        print('({}) {} '.format(i+1,matches[i]) )
    print('({}) Nenhuma deles acima.'.format(num_options))
    ans = False
    while not ans:
        ans = input('Insira o número correspondente à sua resposta: ')
        try:
            ans = int(ans)
            assert(ans in range(1,num_options+1))
        except:
            print('Por favor, insira um númer entre '
                  '1 e {}.'.format(len(matches)+1))
            ans = False
    print('ans = {}, num_opts = {}'.format(ans,num_options))
    if ans == num_options:
        pairs = pairs[pairs.p != p]  # Drop all matches with that name.
    else:
        print('else statement activated')
        n = matches[ans-1]
        pairs = pairs[((pairs.n != n) & (pairs.p != p))     # Drop all except
                      | ((pairs.n == n) & (pairs.p == p))]  # the correct pair.


# Test data for this section:
# 2 people with identical names and different IDs:
# - Both appear on provas, with their IDs; one appears on notas, without ID
# - and another name with same but switch notas/provas
# 1 person with non-similar names on each list, but same ID on each list
# and whose name is similar to other peoples names who dont have ID
# 1 person in provas with 3 similar names on notas, one of which has a non-
# matching ID, the other two with no ID.
# 2 people with similar names, no IDs in notas or provas
                  

#%% Finally, assign unique UIDs to the matches found
        
for n in pairs.n:
    for p in pairs.p[pairs.n == n]:
        notas.UID[notas.nameid == n] = UID
        provas.UID[provas.nameid == p] = UID
        UID += 1
#%%
# ...and give unique UIDs to the remaining students:
        
x = notas.UID[notas.UID.isna()]
UIDs = [UID+i for i in range(len(x))]
notas.UID[notas.UID.isna()] = UIDs
UID += len(x)

y = provas.UID[provas.UID.isna()]
UIDs = [UID+i for i in range(len(y))]
provas.UID[provas.UID.isna()] = UIDs
UID += len(y)

#%% COMBINE DATA: 

# Restore the IDs
notas.ID[notas.ID == 'desconhecido'] = np.nan
provas.ID[provas.ID == 'desconhecido'] = np.nan

#%%
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
    notas.ID[notas.UID == u] = u_ids[u]
    provas.ID[provas.UID == u] = u_ids[u]

#%% Make final merged table
    
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

#%% SAVE FILES
final.to_csv(filepath + '\\combined.csv', na_rep = '#N/A')

