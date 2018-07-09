def get_tokens(): ## Leitura de tokens
    list = []
    while True:
        a = input()
        if a == '':
            break
        list.append(a)
    return list

def get_er(): ## Leitura de exprecoes regulares
    list = []
    while True:
        a = input()
        if a == '':
            break
        list.append(a)
    return list

def add_token(A, token): ## Adiciona todos os tokens em um automato A
    p = 0
    for i in token:
        prod = A[p]
        if prod != '':
            prod += ' '
        prod += i + '<' + str(len(A)) + '>' 
        A[p] = prod
        p = len(A)
        A.append('<'+ str(p) + '> ::=')
    A[len(A)-1] += ' eps'
    return A

def add_er(A, er): ## Adiciona as expressoes regulares no automato A, duplica <S> para <S'> caso a expressao regular aceite retorno a <S> em alguma producao
    for i in er:
        p = ''
        for j in i:
            p+= j
            if j == 'S':
                p+= '\''
        if i[1] == 'S':
            prod = A[0]
            prod += p[8:]
            A[0] = prod
        A.append(p)
    return A

def find_epsT(prod, A): ## Encontra as epsilon transicoes, se houver, no automato A
    for i in range(len(A)):
        for j in range(len(prod)):
            if prod[j][0] in A[i] and prod[j][0] != A[i]:
                prod[i].append(prod[j][0])
    return prod

def get_prod(p, prod): ## Retorna uma producao p em A(prod)
    for i in range(len(prod)):
        if prod[i][0] == p:
            return prod[i]
    return []
 
def find_tI(prod): ## Adiciona todas as producoes de <A> em <S> caso <S> tenha uma epsilon transicao <A>
    flag = True
    while flag:
        flag = False
        for p in prod:
            for i in p:
                prod_i = get_prod(i, prod)
                for j in prod_i:
                    if j not in p:
                        flag = True
                        p.append(j)
    return prod

def clear_epsT(A): ## Executa as funcoes acima e remove as epsilon transicoes
    prod = []
    for i in A:
        prod.append(i[0].split())
    prod = find_epsT(prod, A)
    prod = find_tI(prod)
    for i in range(len(A)):
        p = A[i]
        for j in prod[i]:
            prod_ = get_prod(j, A)
            for k in prod_[2:]:
                if k not in p:
                    p.append(k)
        A[i] = p
    for i in range(len(A)):
        for j in range(len(prod)):
            if prod[j][0] in A[i][2:]:
                A[i].remove(prod[j][0])
    return A

def get_sf(A): ## Retorna uma lista com os simbolos finais
    sf = []
    for i in A:
        for j in i[2:]:
            if j == 'eps' or j == '|':
                continue
            if j[0] not in sf: 
                sf.append(j[0])
    return sf

def create_p(len_sf): ## Cria uma lista com strings vazias do tamanho da lista dos simbolos finais
    p = []
    for i in range(len_sf):
        p.append('')
    return p

def fixup_p(prod):  ## Ajusta o nome das producoes no AFD, para estado de erro ou cria uma producao com um '-' na frente se ela não existisse
    for i in range(len(prod)):
        if prod[i] == '':
            prod[i] = '-'
        if ' ' in prod[i]:
            p = '-'
            for j in sorted(prod[i]):
                if j == ' ':
                    continue
                p += j
            prod[i] = p
    return prod

def clear_p(prod): ## Remove os espacos de uma lista prod
    p = ''
    for i in prod:
        if i == ' ':
            continue
        p += i
    return p

def check_prod(prod, p, test): ## Verifica se uma producao p já pertence ao conjuto das producoes do AFD
    i = '<'
    if test:
        i += '-'
    p = i + p + '>'
    return p in prod

def error_p(n): ## Cria um estado de erro
    error = ['<->']
    error_p = []
    for i in range(n):
        error_p.append('-')
    error.append(error_p)
    return error

def find_p(producoes_p, producao, A, sf): ## Adiciona as producoes da 'producao' em 'producoes_p'
    ignore = ['eps', '|', '::=']
    producao = get_prod( producao, A)
    for i in producao[1:]:
        if i in ignore:
            continue
        indice_p = sf.index(i[0])
        if i[2:-1] in producoes_p[indice_p]:
            continue
        if producoes_p[indice_p] != '':
            producoes_p[indice_p] += ' '
        producoes_p[indice_p] += i[2:-1]
    return producoes_p

def find_new_p(producoes_p, fila, prod): ## Verifica se alguma producao de 'producoes_p' nao pertence ao conjunto de producoes de AFD e coloca em uma fila
    for i in producoes_p:
        if i == '':
            continue
        if ' ' in i:
            j = True
        else:
            j = False
        if not check_prod(prod, i, j):
            fila.insert(0, i)
    return fila


def determinizacao(A): ## Vare o automato aplicando o processo de determinizacao
    sf = sorted(get_sf(A))
    fila = []
    afd = []
    producoes_AFD = []
    for i in A:
        producoes_AFD.append(i[0])
    for i in A:
        producao = [i[0]]
        if 'eps' in i:
            producao.insert(0, '*')
        producoes_p = create_p(len(sf))
        producoes_p = find_p(producoes_p, i[0], A, sf)
        fila = find_new_p(producoes_p, fila, producoes_AFD)
        producao.append(fixup_p(producoes_p))
        afd.append(producao)
    while fila != []:
        p = fila.pop()
        p_split = p.split()
        p = clear_p(sorted(p))
        if check_prod(producoes_AFD, p, True):
            continue
        p = '<-' + p + '>'
        producoes_AFD.append(p)
        producao = [p]
        producoes_p = create_p(len(sf))
        for i in p_split:
            prod_i = get_prod('<' + i + '>', A)
            if 'eps' in prod_i and '*' not in producao:
                producao.insert(0, '*')
            producoes_p = find_p(producoes_p, '<' + i + '>', A, sf)
        fila = find_new_p(producoes_p, fila, producoes_AFD)
        producao.append(fixup_p(producoes_p))
        afd.append(producao)
    
    afd.append(error_p(len(sf)))
    return afd

## fixup_afd nao foi utilizada nesse codigo, removida aqui.

def check_p(check, p, AFD): ## retorna os simbolos visitados a partir de um producao
    check.append(p)
    for i in AFD:
        if '<' + p + '>' in i:
            if len(i) == 2:
                producoes = i[1]
            else:
                producoes = i[2]
            break
    for i in range(len(producoes)):
        if producoes[i] not in check:
            check += set(check_p(check, producoes[i], AFD))
    return check

def minimizacao(AFD): ## Remove os simbolos inalcancaveis mas nao remove os mortos
    check = set(check_p([],'S',AFD))
    remove_p = []
    for i in range(len(AFD)):
        flag = True
        for j in check:
            if '<' + j + '>' in AFD[i]:
                flag = False
        if flag:
            remove_p.append(i)
        else:
            if len(AFD[i]) == 2:
                producoes = AFD[i][1]
            else:
                producoes = AFD[i][2]
            for j in range(len(producoes)):
                if producoes[j] not in check:
                    producoes[j] = '-'

    for i in remove_p:
        AFD.remove(AFD[i])
    return AFD
    
        
tokens = get_tokens()
er = get_er()
A = []
A.append('<S> ::=')
for i in tokens:
    A = add_token(A, i)
A = add_er(A, er)
for i in range(len(A)):
    A[i] = A[i].split()  
A = clear_epsT(A)
AFD = determinizacao(A)
AFD = minimizacao(AFD)
for i in AFD:
    print(i)
