import gc

from formula_utils import *
from utils import new_deepcopy


__author__ = 'thiagovieira'


def build_initial_tableau(formula_list):
    '''
    :param formula_list: List list of parsetree_list representing all initial formulas in NNF
    :return: Dict of tableaux with all rules applied to its branchs in tableaux_dict['tableaux']
    '''
    formulae = []
    for formula in formula_list:
        if not [f for f in formulae if f['formula'] == formula]:  # check duplicate
            formula_dict = {'formula': formula, 'alpha-visited': False,
                            'beta-visited': False,
                            'sub-complete-visited': False}
            formulae.append(formula_dict)
    tableau_dict = {'formulae': formulae, 'is_proper': False,
                    'was_modified': True}
    tableaux = []
    tableaux.append(tableau_dict)
    tableaux_dict = {'tableaux': tableaux, 'was_modified': True}
    if is_proper(tableaux_dict['tableaux'][0]):
        tableaux_dict['tableaux'][0]['is_proper'] = True
        return tableaux_dict
    else:
        return None


def get_tableaux(formula_list, belief):
    '''
    :param formula_list: List list of parsetree_list representing all initial formulas in NNF
    :param belief: Boolean if it is to use logic of belief
    :return: List of tableaux with all rules applied to its branches
    '''
    tableaux_dict = build_initial_tableau(formula_list)
    if tableaux_dict:
        while tableaux_dict['was_modified']:
            tableaux_dict['was_modified'] = False
            tableaux_dict = apply_alpha_rules(tableaux_dict, belief)
            tableaux_dict = apply_beta_rules(tableaux_dict)
            tableaux_dict = get_subformula_complete(tableaux_dict)
        return tableaux_dict['tableaux']
    else:
        return None


def get_subformula_complete(tableaux_dict):
    '''
    :param tableaux_dict: Dict tableaux dict structure with a list of tableau and some global attributes
    :return: Dict of tableaux with all its branches as subformula complete
    '''

    for tableau in tableaux_dict['tableaux']:
        for formula in tableau['formulae']:
            if is_knowledge(formula['formula']) and not formula['sub-complete-visited']:
                formula['sub-complete-visited'] = True
                subformulae_parsetree_list = get_subformulae_recursive(formula['formula'], [])
                for sub_parsetree in subformulae_parsetree_list[1:]:  # remove the original formula
                    if is_knowledge(sub_parsetree) and sub_parsetree[0][1:] == formula['formula'][0][1:]:
                        negated_sub_parsetree = get_negation(sub_parsetree)
                        if (not [f for f in tableau['formulae'] if f['formula'] == sub_parsetree]) and (not [f for f in tableau['formulae'] if f['formula'] == negated_sub_parsetree]):
                            sub_dict = {'formula': sub_parsetree,
                                        'alpha-visited': False,
                                        'beta-visited': False,
                                        'sub-complete-visited': False}
                            negated_sub_dict = {'formula': negated_sub_parsetree,
                                        'alpha-visited': False,
                                        'beta-visited': False,
                                        'sub-complete-visited': False}
                            tableaux_dict['was_modified'] = True
                            new_tableau = new_deepcopy(tableau)
                            tableau['formulae'].append(sub_dict)  # added on current tableau
                            new_tableau['formulae'].append(negated_sub_dict)  # added on a new tableau
                            tableaux_dict['tableaux'].append(new_tableau)
    return tableaux_dict


def apply_alpha_rules(tableaux_dict, belief):
    '''
    :param tableaux_dict: Dict tableaux dict structure with a list of tableau and some global attributes
    :param belief: Boolean if it is to use logic of belief
    :return: Dict of tableaux with all alpha rules applied to its branches in tableaux_dict['tableaux']
    '''
    for tableau in tableaux_dict['tableaux']:
        is_proper_tableau = True
        for formula in tableau['formulae']:
            if not formula['alpha-visited']:
                formula['alpha-visited'] = True
                if is_conjuction(formula['formula']):
                    alpha1_dict = {'formula': formula['formula'][0][1],
                                   'alpha-visited': False,
                                   'beta-visited': False,
                                   'sub-complete-visited': False}
                    alpha2_dict = {'formula': formula['formula'][0][3],
                                   'alpha-visited': False,
                                   'beta-visited': False,
                                   'sub-complete-visited': False}
                    if not [f for f in tableau['formulae'] if f['formula'] == alpha1_dict['formula']]:  # check duplicate
                        tableau['was_modified'] = True
                        tableau['formulae'].append(alpha1_dict)
                        is_proper_tableau = is_proper(tableau)
                    if not [f for f in tableau['formulae'] if f['formula'] == alpha2_dict['formula']]:  # check duplicate
                        tableau['was_modified'] = True
                        tableau['formulae'].append(alpha2_dict)
                        is_proper_tableau = is_proper(tableau)
                elif is_always(formula['formula']) or is_knowledge(formula['formula']):
                    if is_always(formula['formula']):
                        alpha1 = formula['formula'][1]
                        alpha1_dict = {'formula': alpha1,
                                       'alpha-visited': False,
                                       'beta-visited': False,
                                       'sub-complete-visited': False}
                        alpha2_string = '[\'N\',' + str(formula['formula']) + ']'
                        alpha2 = literal_eval(alpha2_string)
                        alpha2_dict = {'formula': alpha2,
                                       'alpha-visited': False,
                                       'beta-visited': False,
                                       'sub-complete-visited': False}
                        if not [f for f in tableau['formulae'] if f['formula'] == alpha1_dict['formula']]:  # check duplicate
                            tableau['was_modified'] = True
                            tableau['formulae'].append(alpha1_dict)
                            is_proper_tableau = is_proper(tableau)
                        if not [f for f in tableau['formulae'] if f['formula'] == alpha2_dict['formula']]:  # check duplicate
                            tableau['was_modified'] = True
                            tableau['formulae'].append(alpha2_dict)
                            is_proper_tableau = is_proper(tableau)
                    else:  # is_knowledge
                        if not belief:
                            tableau['was_modified'] = True
                            alpha1 = formula['formula'][1]
                            alpha1_dict = {'formula': alpha1,
                                           'alpha-visited': False,
                                           'beta-visited': False,
                                           'sub-complete-visited': False}
                            if not [f for f in tableau['formulae'] if f['formula'] == alpha1_dict['formula']]:  # check duplicate
                                tableau['was_modified'] = True
                                tableau['formulae'].append(alpha1_dict)
                                is_proper_tableau = is_proper(tableau)
                if not is_proper_tableau:
                    tableaux_dict['tableaux'].remove(tableau)
                    gc.collect()  # to avoid list fragmentation
                    break
    return tableaux_dict


def apply_beta_rules(tableaux_dict):
    '''
    :param tableaux_dict: Dict tableaux dict structure with a list of tableau and some global attributes
    :return: Dict of tableaux with all beta rules applied to its branches in tableaux_dict['tableaux']
    '''
    for tableau in tableaux_dict['tableaux']:
        is_proper_tableau = True
        if tableau['was_modified']:
            tableau['was_modified'] = False
            for formula in tableau['formulae']:
                if not formula['beta-visited']:
                    formula['beta-visited'] = True
                    if is_until(formula['formula']) or is_unless(formula['formula']):
                        beta1 = formula['formula'][0][3]
                        beta1_dict = {'formula': beta1, 'alpha-visited': False,
                                      'beta-visited': False,
                                      'sub-complete-visited': False}
                        beta2_string = '[[\'binary\',[[\'binary\',[\'~\',' + \
                                       str(formula['formula'][0][3]) + '],\'^\',' + \
                                       str(formula['formula'][0][1]) + ']],\'^\',[\'N\',[' + \
                                       str(formula['formula'][0]) + ']]]]'
                        beta2 = literal_eval(beta2_string)
                        beta2_dict = {'formula': get_NNF_recursive(beta2),
                                      'alpha-visited': False,
                                      'beta-visited': False,
                                      'sub-complete-visited': False}  # as we negate some formula, we have to ensure that it still remain in NNF
                        if not [f for f in tableau['formulae'] if f['formula'] == beta2_dict['formula']]:  # check duplicate
                            tableaux_dict['was_modified'] = True
                            tableau['was_modified'] = True
                            new_tableau = new_deepcopy(tableau)
                            new_tableau['formulae'].append(
                                beta2_dict)  # added on a new tableau
                            if is_proper(new_tableau):
                                tableaux_dict['tableaux'].append(new_tableau)
                        if not [f for f in tableau['formulae'] if f['formula'] == beta1_dict['formula']]:  # check duplicate
                            tableaux_dict['was_modified'] = True
                            tableau['was_modified'] = True
                            tableau['formulae'].append(beta1_dict)  # added on current tableau
                            is_proper_tableau = is_proper(tableau)
                    elif is_eventually(formula['formula']):
                        beta1 = formula['formula'][1]
                        beta1_dict = {'formula': beta1, 'alpha-visited': False,
                                      'beta-visited': False,
                                      'sub-complete-visited': False}
                        beta2_string = '[[\'binary\',[\'~\',' + \
                                       str(formula['formula'][1]) + '],\'^\',' + '[\'N\',' + \
                                       str(formula['formula']) + ']]]'
                        beta2 = literal_eval(beta2_string)
                        beta2_dict = {'formula': get_NNF_recursive(beta2),
                                      'alpha-visited': False,
                                      'beta-visited': False,
                                      'sub-complete-visited': False}  # as we negate some formula, we have to ensure that it still remains in NNF
                        if not [f for f in tableau['formulae'] if f['formula'] == beta2_dict['formula']]:  # check duplicate
                            tableaux_dict['was_modified'] = True
                            tableau['was_modified'] = True
                            new_tableau = new_deepcopy(tableau)
                            new_tableau['formulae'].append(
                                beta2_dict)  # added on a new tableau
                            if is_proper(new_tableau):
                                tableaux_dict['tableaux'].append(new_tableau)
                        if not [f for f in tableau['formulae'] if f['formula'] == beta1_dict['formula']]:  # check duplicate
                            tableaux_dict['was_modified'] = True
                            tableau['was_modified'] = True
                            tableau['formulae'].append(beta1_dict)  # added on current tableau
                            is_proper_tableau = is_proper(tableau)
                    elif is_disjunction(formula['formula']):
                        beta1_dict = {'formula': formula['formula'][0][1],
                                      'alpha-visited': False,
                                      'beta-visited': False,
                                      'sub-complete-visited': False}
                        beta2_dict = {'formula': formula['formula'][0][3],
                                      'alpha-visited': False,
                                      'beta-visited': False,
                                      'sub-complete-visited': False}
                        if not [f for f in tableau['formulae'] if f['formula'] == beta2_dict['formula']]:  # check duplicate
                            tableaux_dict['was_modified'] = True
                            tableau['was_modified'] = True
                            new_tableau = new_deepcopy(tableau)
                            new_tableau['formulae'].append(beta2_dict)  # added on a new tableau
                            if is_proper(new_tableau):
                                tableaux_dict['tableaux'].append(new_tableau)
                        if not [f for f in tableau['formulae'] if f['formula'] == beta1_dict['formula']]:  # check duplicate
                            tableaux_dict['was_modified'] = True
                            tableau['was_modified'] = True
                            tableau['formulae'].append(beta1_dict)  # added on current tableau
                            is_proper_tableau = is_proper(tableau)
                    if not is_proper_tableau:
                        tableaux_dict['tableaux'].remove(tableau)
                        gc.collect()  # to avoid list fragmentation
                        break
    return tableaux_dict



def is_proper(tableau):
    '''
    Loop through formulae in reverse mode. Based on tableau construction, small formulae should be at the end of it
    :param tableau: Dict tableau dict structure with a list of formulae and some attributes
    :return: Boolean  True if is proper, False otherwise
    '''
    for index, pivot_formula in reversed(list(enumerate(tableau['formulae']))):
        if is_false(pivot_formula['formula']):
            return False
        elif is_atom(pivot_formula['formula']) or is_knowledge(pivot_formula['formula']):
            is_positive = True
        elif is_negated_unary_or_atom(pivot_formula['formula'],'atom') or \
                is_negated_unary_or_atom(pivot_formula['formula'], 'knowledge'):
            is_positive = False
        else:
            continue
        if index > 0:
            for formula in reversed(tableau['formulae'][:index]):
                if is_positive and \
                        (is_negated_unary_or_atom(formula['formula'], 'atom') or
                             is_negated_unary_or_atom(formula['formula'], 'knowledge')):
                    if str(pivot_formula['formula']) == str(formula['formula'][1]):
                        return False
                elif not is_positive and (is_atom(formula['formula']) or is_knowledge(formula['formula'])):
                    if str(pivot_formula['formula'][1]) == str(formula['formula']):
                        return False
                else:
                    continue
    return True


if __name__ == '__main__':
    formula_list = []
    # formula_list = [[['binary', [['binary', [['binary', ['p0'], '^', ['p9']]], '^', ['r5']]], '^', [['binary', ['t9'], '^', ['q3']]]]]] #(p0^p9)^r5^(t9^q3)
    # formula_list.append([['binary', ['p0'], 'v', ['p0']]])
    #formula_list.append([['binary', ['p0'], 'v', ['p0']]])
    #formula_list.append([['binary', ['p0'], '^', ['~',['p9']]]])
    #formula_list.append([['binary', ['p0'], '^', ['~',['p9']]]])
    # formula_list = [[['binary', [['binary', ['p0'], 'v', ['p9']]], '^', ['t5']]]]
    # formula_list = [[['binary', [['binary', ['p0'], '^', ['p9']]], 'v', ['t5']]]]
    # formula_list.append(['G', [['binary', ['p0'], '^', ['p0']]]])
    #formula_list.append(['G', [['binary', ['p0'], '^', ['p0']]]])
    #formula_list = [[['binary', ['p0'], 'W', ['q9']]]]
    #formula_list.append(['F', ['~', ['p0']]])
    # formula_list.append(['~', ['p0']])
    #formula_list.append([['binary', [['binary', ['p0'], 'v', ['~', ['p1']]]], '^', ['p1']]])
    belief = False
    tableaux = get_tableaux(formula_list, belief)
    for index, tableau in enumerate(tableaux):
        print 'is proper: ' + str(is_proper(tableau))
        print 'tableau branch: ' + str(index)
        for formula in tableau['formulae']:
            print formula['formula']
        print '--------------------------'
