import cProfile
from ast import literal_eval

from utils import *


__author__ = 'thiagovieira'

'''
Auxiliary formula functions
'''


def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()

    return profiled_func


def parsetree_string_to_list(parsetree_string):
    '''
    Modify tuple string returned by grammar parse to a list without unnecessary tokens
    and brackets
    :param parsetree_string: String tree tuple string from grammar parser
    :return: List Python list representation of parsetree_string
    '''
    parsetree_string = ' '.join(
        parsetree_string.split())  # remove multiples whitspaces
    parsetree_string = parsetree_string.replace('(START', '')[:-1]
    parsetree_string = parsetree_string.replace(' (formula \'(\' ', ',(')\
                                        .replace(' \')\'', '')\
                                        .replace('(unary ', '') \
                                        .replace('binary', '\'binary\'')\
                                        .replace('(atom ', '')\
                                        .replace('\')', '\'')\
                                        .replace(' ', ',')\
                                        .replace('(', '[') \
                                        .replace(')', ']') \
                                        .replace('formula,', '')[1:]
    parsetree_list = literal_eval(parsetree_string)
    return parsetree_list


def parsetree_list_to_string_with_parentheses(parsetree_list):
    '''
    :param parsetree_list: List tree representation of the string formula
    :return: String formula representation as string with parentheses
    '''
    parsetree_string = str(parsetree_list)
    parsetree_string = parsetree_string.replace('[[\'binary\',', '[') \
        .replace(',', '') \
        .replace('\'', '') \
        .replace(']]', ']') \
        .replace('[', '(') \
        .replace(']', ')')
    return parsetree_string



def get_main_operator(parsetree_list):
    '''
    :param parsetree_list: List tree representation of the string formula
    :return: String main operator operator as string
    '''
    if is_atom(parsetree_list):
        return parsetree_list[0]
    elif is_unary(parsetree_list):
        return parsetree_list[0]
    elif is_binary(parsetree_list):
        return parsetree_list[0][2]


def get_subformulae_recursive(parsetree_list, subformulae_list):
    '''
    :param parsetree_list: List tree representation of the string formula
    :param subformulae_list: List of subformulae as parsetree list
    :return: List of subformulae as parsetree list
    '''
    subformulae_list.append(parsetree_list)
    if is_binary(parsetree_list):
        left = parsetree_list[0][1]
        right = parsetree_list[0][3]
        get_subformulae_recursive(left, subformulae_list)
        get_subformulae_recursive(right, subformulae_list)
    elif is_unary(parsetree_list):
        get_subformulae_recursive(parsetree_list[1], subformulae_list)
    else:  # is_atom
        return
    return subformulae_list


def apply_nnf_to_parsetree_list_list(parsetree_list_list):
    formulae_list = []
    for parsetree_list in parsetree_list_list:
        parsetree_list_nnf = get_NNF_recursive(parsetree_list)
        parsetree_list_sorted = sort_recursive(parsetree_list_nnf)
        formulae_list.append(parsetree_list_sorted)
    return formulae_list


# @do_cprofile
def get_NNF_recursive(parsetree_list):
    '''
    Get negation normal form from a parsetree list WITH NO IMPLICATIONS
    :param parsetree_list: List tree representation of the string formula with no implications
    :return: List parsetree list in negation normal form
    '''
    parsetree_string = ''
    if is_binary(parsetree_list):
        left = '[[\'binary\',' + str(get_NNF_recursive(parsetree_list[0][1]))
        main_operator = ',\'' + get_main_operator(parsetree_list) + '\','
        right = str(get_NNF_recursive(parsetree_list[0][3])) + ']]'
        parsetree_string = left + main_operator + right
    elif is_unary(parsetree_list):
        if is_negation(parsetree_list):
            if is_binary(parsetree_list[1]):
                new_parsetree_list = propagate_negation_binary(parsetree_list)
                parsetree_string = str(get_NNF_recursive(new_parsetree_list))
            elif is_unary(parsetree_list[1]):
                if is_negation(parsetree_list[1]):
                    parsetree_string = str(get_NNF_recursive(parsetree_list[1][1]))
                else:
                    if is_knowledge(parsetree_list[1]):
                        parsetree_string = '[\'~\',' + str(get_NNF_recursive(parsetree_list[1])) + ']'
                    else:
                        new_parsetree_list = propagate_negation_unary(parsetree_list)
                        parsetree_string = str(get_NNF_recursive(new_parsetree_list))
            else:  # negated atom
                parsetree_string = str(parsetree_list)
        else:
            parsetree_string = '[\'' + str(parsetree_list[0]) + '\',' + str(get_NNF_recursive(parsetree_list[1])) + ']'
    else:  # atom case
        parsetree_string = str(parsetree_list)
    new_parsetree_list = literal_eval(parsetree_string)
    return new_parsetree_list


def propagate_negation_binary(unary_parsetree_list):
    '''
    Propagate negation in one step on binary formulae
    :param unary_parsetree_list: List tree representation of the string formula
    :return: List parsetree list with negation propagated one step
    '''
    new_parsetree_string = ''
    # if is_binary(unary_parsetree_list[1]): already executed before call this function
    if is_conjuction(unary_parsetree_list[1]):
        new_parsetree_string = apply_de_morgan(unary_parsetree_list[1], '^')
    elif is_disjunction(unary_parsetree_list[1]):
        new_parsetree_string = apply_de_morgan(unary_parsetree_list[1], 'v')
    elif is_until(unary_parsetree_list[1]):
        new_parsetree_string = apply_modal_de_morgan(unary_parsetree_list[1], 'U')
    else:  # unless
        new_parsetree_string = apply_modal_de_morgan(unary_parsetree_list[1], 'W')
    return literal_eval(new_parsetree_string)


def propagate_negation_unary(unary_parsetree_list):
    '''
    Propagate negation in one step on unary formulae
    :param unary_parsetree_list: List tree representation of the string formula
    :return: List parsetree list with negation propagated one step
    '''
    new_parsetree_string = ''
    # if is_unary(unary_parsetree_list[1]): already executed before call this function
    if is_always(unary_parsetree_list[1]):
        new_parsetree_string = '[\'F\',[\'~\',' + str(unary_parsetree_list[1][1]) + ']]'
    elif is_eventually(unary_parsetree_list[1]):
        new_parsetree_string = '[\'G\',[\'~\',' + str(unary_parsetree_list[1][1]) + ']]'
    else:  # is_next(unary_parsetree_list[1]):
        new_parsetree_string = '[\'N\',[\'~\',' + str(unary_parsetree_list[1][1]) + ']]'
    return literal_eval(new_parsetree_string)


def apply_de_morgan(parsetree_list, connective):
    '''
    :param parsetree_list: List BINARY formula parsetree list
    :param connective: String main operator of bynary formula
    :return: String string representation of the new binary formula with de morgan rule applied
    '''
    if connective == 'v':
        new_main_operator = ',\'^\','
    elif connective == '^':
        new_main_operator = ',\'v\','
    elif connective == 'U':
        new_main_operator = ',\'W\','
    else:
        new_main_operator = ',\'U\','
    new_left = '[[\'binary\',[\'~\',' + str(parsetree_list[0][1]) + ']'
    new_right = '[\'~\',' + str(parsetree_list[0][3]) + ']]]'
    new_parsetree_string = new_left + new_main_operator + new_right
    return new_parsetree_string


def apply_modal_de_morgan(parsetree_list, connective):
    '''
    :param parsetree_list: List BINARY formula parsetree list
    :param connective: String main operator of bynary formula
    :return: String string representation of the new binary formula with de morgan rule applied
    '''
    if connective == 'U':
        new_main_operator = ',\'W\','
    else:
        new_main_operator = ',\'U\','
    new_left = '[[\'binary\',[\'~\',' + str(parsetree_list[0][3]) + ']'
    new_right = '[[\'binary\',[\'~\',' + str(parsetree_list[0][1]) + '],\'^\',[\'~\',' + str(parsetree_list[0][3]) + ']]]]]'
    new_parsetree_string = new_left + new_main_operator + new_right
    return new_parsetree_string


# @do_cprofile
def remove_implications_recursive(parsetree_list):
    '''
    :param parsetree_list: List tree representation of the string formula
    :return: List new parsetree list with no implications
    '''
    #parsetree_list = clean_brackets_parsetree_list(parsetree_list)
    if is_binary(parsetree_list):
        left = parsetree_list[0][1]
        main_operator = get_main_operator(parsetree_list)
        right = parsetree_list[0][3]
        if main_operator == '->':
            new_left = '[[\'binary\',[\'~\',' + str(left) + ']'
            new_main_operator = ',\'v\','
            new_right = str(right) + ']]'
            new_parsetree_string = new_left + new_main_operator + new_right
            new_parsetree_list = literal_eval(new_parsetree_string)
            return remove_implications_recursive(new_parsetree_list)
        else:
            new_left = '[[\'binary\',' + str(
                remove_implications_recursive(left))
            new_main_operator = ',\'' + main_operator + '\','
            new_right = str(remove_implications_recursive(right)) + ']]'
            new_parsetree_string = new_left + new_main_operator + new_right
            new_parsetree_list = literal_eval(new_parsetree_string)
            return new_parsetree_list
    elif is_unary(parsetree_list):
        new_parsetree_string = '[\'' + str(
            parsetree_list[0]) + '\',' + str(
            remove_implications_recursive(parsetree_list[1])) + ']'
        new_parsetree_list = literal_eval(new_parsetree_string)
        return new_parsetree_list
    else:  # atom case
        return parsetree_list


def is_unary(parsetree_list):
    '''
    Check if is unary at the start or in subformulas
    :param parsetree_list: List tree representation of the string formula
    :return: True if is unary, False otherwise
    '''
    if any((c in ['k', 'N', 'F', 'G', '~']) for c in parsetree_list[0][0]):
        return True
    else:
        return False


def is_binary(parsetree_list):
    '''
    :param parsetree_list: List tree representation of the string formula
    :return: True if is binary, False otherwise
    '''
    if 'binary' in parsetree_list[0][0]:
        return True
    else:
        return False


def is_atom(parsetree_list):
    '''
    :param parsetree_list: List tree representation of the string formula
    :return: True if is atom, False otherwise
    '''
    if not is_binary(parsetree_list) and not is_unary(parsetree_list):
        return True
    else:
        return False


def is_false(parsetree_list):
    '''
    Should be called after or in conjunction with is_unary
    :param parsetree_list:List tree representation of the string formula
    :return: True if is false constant, False otherwise
    '''
    if get_main_operator(parsetree_list) == 'false':
        return True
    else:
        return False


def is_true(parsetree_list):
    '''
    Should be called after or in conjunction with is_unary
    :param parsetree_list:List tree representation of the string formula
    :return: True if is true constant, False otherwise
    '''
    if get_main_operator(parsetree_list) == 'true':
        return True
    else:
        return False


def is_negation(parsetree_list):
    '''
    Should be called after or in conjunction with is_unary
    :param parsetree_list:List tree representation of the string formula
    :return: True if is negation, False otherwise
    '''
    if get_main_operator(parsetree_list) == '~':
        return True
    else:
        return False


def is_prop(parsetree_list):
    '''
    :param parsetree_list:List tree representation of the string formula
    :return: True if is propositional symbol, False otherwise
    '''
    pass


def is_knowledge(parsetree_list):
    '''
    :param parsetree_list:List tree representation of the string formula
    :return: True if is knowledge formulae, False otherwise
    '''
    if 'k' in get_main_operator(parsetree_list):
        return True
    else:
        return False


def is_always(parsetree_list):
    '''
    :param parsetree_list:List tree representation of the string formula
    :return: True if is always formulae, False otherwise
    '''
    if get_main_operator(parsetree_list) == 'G':
        return True
    else:
        return False


def is_eventually(parsetree_list):
    '''
    :param parsetree_list:List tree representation of the string formula
    :return: True if is eventually formulae, False otherwise
    '''
    if get_main_operator(parsetree_list) == 'F':
        return True
    else:
        return False


def is_next(parsetree_list):
    '''
    :param parsetree_list:List tree representation of the string formula
    :return: True if is next formulae, False otherwise
    '''
    if get_main_operator(parsetree_list) == 'N':
        return True
    else:
        return False


def is_conjuction(parsetree_list):
    '''
    Should be called after or in conjunction with is_binary
    :param parsetree_list:List tree representation of the string formula
    :return: True if is a conjunction, False otherwise
    '''
    if get_main_operator(parsetree_list) == '^':
        return True
    else:
        return False


def is_disjunction(parsetree_list):
    '''
    Should be called after or in conjunction with is_binary
    :param parsetree_list:List tree representation of the string formula
    :return: True if is a disjunction, False otherwise
    '''
    if get_main_operator(parsetree_list) == 'v':
        return True
    else:
        return False


def is_until(parsetree_list):
    '''
    Should be called after or in conjunction with is_binary
    :param parsetree_list:List tree representation of the string formula
    :return: True if is a until, False otherwise
    '''
    if get_main_operator(parsetree_list) == 'U':
        return True
    else:
        return False


def is_unless(parsetree_list):
    '''
    Should be called after or in conjunction with is_binary
    :param parsetree_list:List tree representation of the string formula
    :return: True if is a unless, False otherwise
    '''
    if get_main_operator(parsetree_list) == 'W':
        return True
    else:
        return False


def is_negated_unary_or_atom(parsetree_list, something):
    '''
    :param parsetree_list:  List tree representation of the string formula
    :param something: String type of unary formula
    :return: Boolean True if is negated knowledge, False otherwise
    '''
    is_something = {
        'knowledge': is_knowledge,
        'atom': is_atom,
        'always': is_always,
        'eventually': is_eventually,
        'next': is_next
    }.get(something)
    if is_something and (is_atom(parsetree_list) or is_unary(parsetree_list)):
        if is_negation(parsetree_list):
            if is_something(parsetree_list[1]):
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def get_negation(parsetree_list):
    '''
    :param parsetree_list: List tree representation of the string formula
    :return: List tree representation of the negated string formula
    '''
    parsetree_string = '[\'~\',' + str(parsetree_list) + ']'
    new_parsetree_list = literal_eval(parsetree_string)
    return new_parsetree_list


def sort_recursive(parsetree_list):
    '''
    :param parsetree_list: List tree representation of the string formula
    :return: List tree representation of the string formula with conjunctions and disjunctions sorted in lexicographic order
    '''
    if is_binary(parsetree_list):
        left = parsetree_list[0][1]
        main_operator = ',\'' + get_main_operator(parsetree_list) + '\','
        right = parsetree_list[0][3]
        left_string = '[[\'binary\','
        right_string = ']]'
        if is_conjuction(parsetree_list) or is_disjunction(parsetree_list):
            if is_binary(left) and is_binary(right):
                if (is_conjuction(left) or is_disjunction(left)) and (is_conjuction(right) or is_disjunction(right)): #conjunction comes first
                    if (is_conjuction(left) and is_conjuction(right)) or is_disjunction(left) and is_disjunction(right):
                        sorted_left = sort_recursive(left)
                        sorted_right = sort_recursive(right)
                        if str(sorted_left) >= str(sorted_right):
                            left_string =  left_string + str(sort_recursive(sorted_left))
                            right_string = str(sort_recursive(sorted_right)) + right_string
                        else:
                            left_string =  left_string + str(sort_recursive(right))
                            right_string = str(sort_recursive(left)) + right_string
                    elif is_conjuction(left):
                        left_string =  left_string + str(sort_recursive(left))
                        right_string = str(sort_recursive(right)) + right_string
                    else:
                        left_string =  left_string + str(sort_recursive(right))
                        right_string = str(sort_recursive(left)) + right_string
                elif is_conjuction(left) or is_disjunction(left): # conjunctions and disjunctions come first than others binary formulas
                    left_string =  left_string + str(sort_recursive(left))
                    right_string = str(sort_recursive(right)) + right_string
                elif is_conjuction(right) or is_disjunction(right): # conjunctions and disjunctions come first than others binary formulas
                    left_string =  left_string + str(sort_recursive(right))
                    right_string = str(sort_recursive(left)) + right_string
                else: #others binary formulas
                    left_string =  left_string + str(sort_recursive(left))
                    right_string = str(sort_recursive(right)) + right_string
            elif is_binary(left):
                left_string = left_string + str(sort_recursive(right)) #unary/atom comes first
                right_string = str(sort_recursive(left)) + right_string
            elif is_binary(right):
                left_string = left_string + str(sort_recursive(left)) #unary/atom comes first
                right_string = str(sort_recursive(right)) + right_string
            elif is_unary(left) and is_unary(right):
                if str(left[0]) >= str(right[0]):
                    left_string = left_string + '[\'' + str(right[0]) + '\',' + str(sort_recursive(right[1])) + ']'
                    right_string = '[\'' + str(left[0]) + '\',' + str(sort_recursive(left[1])) + ']' + right_string
                else:
                    left_string = left_string + '[\'' + str(left[0]) + '\',' + str(sort_recursive(left[1])) + ']'
                    right_string = '[\'' + str(right[0]) + '\',' + str(sort_recursive(right[1])) + ']' + right_string
            elif is_unary(left):
                left_string = left_string + str(right) #atom comes first
                right_string = '[\'' + str(left[0]) + '\',' + str(sort_recursive(left[1])) + ']' + right_string
            elif is_unary(right):
                left_string = left_string + str(left) #atom comes first
                right_string = '[\'' + str(right[0]) + '\',' + str(sort_recursive(right[1])) + ']' + right_string
            else: #both are atoms
                if str(left[0]) >= str(right[0]):
                    left_string = left_string + str(right)
                    right_string = str(left) + right_string
                else:
                    left_string = left_string + str(left)
                    right_string = str(right) + right_string
            return literal_eval(left_string + main_operator + right_string)
        else:
            left_string = left_string + str(sort_recursive(left))
            right_string = str(sort_recursive(right)) + right_string
            parsetree_string = left_string + main_operator + right_string
            return literal_eval(parsetree_string)
    elif is_unary(parsetree_list):
        return literal_eval('[\'' + str(parsetree_list[0]) + '\',' + str(sort_recursive(parsetree_list[1])) + ']')
    else:
        return parsetree_list


def get_len(parsetree_list):
    '''
    Return the size of a formula without counting brackets, only symbols
    :param parsetree_list: List parsetree list
    :return: Int size of the formula
    '''
    lista = list(flatten(parsetree_list))
    return len(lista)


if __name__ == '__main__':
    lista = []
    # unary
    lista.append(['k3',['p0']])
    # lista.append(['~', ['~', ['~', [['false']]]]])
    #lista.append(['~', ['G', [['binary', [['p9']], '->', [['p0']]]]]])
    #lista.append(['~', [['binary', ['~', [['p0']]], '^', [['p1']]]]])
    #lista.append(['~', [['binary', [['p0']], '->', [['p1']]]]])
    #lista.append(['k3', [['binary', [['binary', ['G', ['t3']], '^', ['r1']]], 'v', ['~', ['k2', ['p2']]]]]])

    # binary
    #lista.append([['binary', ['~', [['binary', ['~', ['~', [['p9']]]], 'v', [['p4']]]]], 'v',
    #               ['F', [['p2']]]]])
    lista.append([['binary', ['~', ['~',['start']]], 'U', ['p1']]])
    lista.append([['binary', ['~', ['p3']], 'v',[['binary', ['p4'], '^', ['p3']]]]])
    lista.append([['binary', ['p9'], '^', ['~',['p5']]]])
    lista.append([['binary', ['p9'], 'v', ['p5']]])

    lista.append([['binary', [['binary', ['p3'], '^', ['p2']]], 'v', [['binary', ['p0'], '^', ['q0']]]]])
    lista.append([['binary', [['binary', ['p0'], '^', ['q0']]], 'v', [['binary', ['p3'], '^', ['p2']]]]])


    #print get_len(lista)
    #print is_negated_unary_or_atom(lista[0], 'gluglu')
    #print is_negated_unary_or_atom(lista[0], 'knowledge')
    #print is_negated_unary_or_atom(lista[0], 'atom')
    #print is_negated_unary_or_atom(lista[0], 'next')
    #print is_negated_unary_or_atom(lista[0], 'eventually')
    #print is_negated_unary_or_atom(lista[0], 'always')

    #parsetree = literal_eval(get_subformulae_recursive(lista[0], [])[0])
    #print parsetree[0][1]
    for f in lista:
        print 'original: ' + str(f)
        sorted_parsetree = sort_recursive(f)
        print 'sorted: ' + str(sorted_parsetree) + str(type(sorted_parsetree))
        print '---------------------------------------'