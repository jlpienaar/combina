# combina

## Português  (Scroll down for English version)
`combina.py` é uma programa símples que pode fundir duas tabelas de notas. Se os números de identidade não são disponíveis, a programa pode identificar os estudantes usando os nomes deles. Os nomes não precisam ser iguais em cada tabela: o algoritmo pode adivinhar quais nomes correspondem à mesma pessoa. Se ele acha vários nomes similares, ele vai pedir para você o ajude.

### Motivação:
Escrevi essa programa para ajudar os assistentes no UFRJ. Eles usam uma plataforma chamado PoliMoodle para gerenciar as notas dos estudantes, que não tem lugar onde estudantes podem entrar seus números de identificação nas notas deles. Como assim, para juntar as notas e as provas, os assistentes tem que identificar cada estudante manualmente, entre duas listes de mais do que 100 nomes, e não todas tem números de identificação. Se você não acho difícil, considera que:

* Não todos os sobrenomes parecem em cada tabela, então pode ter um estudante com nomes que parecem differente, ou dois estudantes com nomes muitos parecidos;

* De fato, há casos em que dois estudantes tem exatamente o mesmo nome nas listas (mesmo com todos os sobrenomes!) e só podem ser differenciados por número de ID.

Isso é uma perda de tempo absurdo. O `combina.py` faz o maior parte do trabalho automaticamente, so pedindo ajuda nos casos de incerteza. Ele pode identificar os estudantes em 96% dos casos, e só vai precisar adjuda em 4% dos casos. Eu acredito que o possibilidade de fazer uma identificação errado é quase 0%; mesmo assim eu recommendo que você verificar os nomes na tabula final.

### Como usar
Para usar a programa, tem que salvar as tabelas como arquivos CSV, nomeados "notas.csv" e "procas.csv", e colocar eles na mesma pasta no seu computador. *Importante:* A primeira coluna de "notas.csv" deve ser os primeiros nomes dos estudantes; a segunda coluna deve ser os sobrenomes, e a terceira deve ser os números de identidade (se houver). Na "provas.csv" a primeira coluna deve ser os nomes inteiros dos estudantes, e a segunda coluna deve ser os números de ID. (Todas outras colunas podem ser qualquer coisa, não importa).

Para iniciar a programa, tem dois métodos. Para quem fica confortável com Python, coloca `combina.py` na mesma pasta com os arquivos CSV, abra um terminal ou command prompt nesse lugar, e bate:

`python combina.py`

Se você não conheço Python, e está usando Windows, eu inclui um arquivo `combina.exe`. Simplesmente coloca ele na mesma pasta com os arquivos CSV, e clique para iniciar.

### Desaprovador legal
Você usa essa programa no seu próprio risco. Eu não tomo responsibilidade de qualquer problema que surge com o use deste software.  

## English
`combina.py` is a simple Python script that merges two tables of students' grades. If student ID numbers are not available, it matches the students by their names in each table. The names in each table do not have to be identical: the algorithm can guess which names correspond to the same person. If it finds multiple possible matches for a student name, it asks for the user's input to resolve the ambiguity.

### Motivation
I wrote this code to help the teaching assistants at UFRJ. They use a system called PoliMoodle for managing students' term grades, which does not provide a place where students can enter their ID numbers when doing tests. This means when it comes time to combine the term grades with the final exam grades, it is left to the teaching assistants to merge two tables of grades, where one of the tables only identifies the students by name. If you think that doesn't sound bad, consider the following complications:

* In Brazil, students have multiple last names, and there is no fixed convention which one to use when asked to enter only one of them;

* Despite having multiple last names, many names are quite common, so it is not unusual to find two students with exactly the same names, eg. Gabriela Moreira da Silva Castro. 

The teaching assistants are forced to merge two excel spreadsheets by hand, which means going through a list of over 100 students' names, finding the matching student from a similar list, and copy-pasting their data into a single table. This is a tragic and unnecessary waste of time. `combina.py` does most of the work automatically, asking for help only in cases where it is not sure how to match the students. Testing it on real student data, it correctly matched about 96% of the students and asked for help for the remaining 4%, meaning that it made zero errors.

### Usage

To use the script you must save the tables as two CSV files, named "notas.csv" and "provas.csv", and place them in the same directory. *Important:* The first column of "notas.csv" must be the first names of the students, the second column must be the surnames, and the third column must be the ID numbers (if any). In "provas.csv" the first column must be the full name of the students, and the second column must be the ID numbers. (All other columns can be anything, it doesn't matter).

To run the script, there are two possible ways. If you are comfortable using python, put the file `combina.py` into the same folder as the CSV files, then open a terminal in that location and type

`python combina.py`

If you are not comfortable using the terminal or command line, and if you are using Windows, I have included an executable file `combina.exe`. Simply put this file in the same folder as the CSV files and double click to execute it.

### Disclaimer
Use this code at your own risk. I don't accept responsibility for anything bad that might happen as a result of you using my code.


