from collections import deque

import networkx as nx

from formula_utils import *
from tableau import get_tableaux

#try:
#    import matplotlib.pyplot as plt
#except:
#    raise


__author__ = 'thiagovieira'


def build_states(tableaux_list):
    '''
    :param tableaux_list: List list of tableau dicts structure with a list of formulae
    :return: List a list of states labelled by their index with all formulae as a list of parsetree list
    '''
    states = []
    agents_list = []
    for tableau in tableaux_list:
        new_state = []
        for formula in tableau['formulae']:
            if is_knowledge(formula['formula']) or is_negated_unary_or_atom(formula['formula'],'knowledge'):
                if is_knowledge(formula['formula']):
                    if str(formula['formula'][0][1:]) not in agents_list:
                        agents_list.append(str(formula['formula'][0][1:]))
                else:
                    if str(formula['formula'][1][0][1:]) not in agents_list:
                        agents_list.append(str(formula['formula'][1][0][1:]))
            new_state.append({'formula':formula['formula'], 'k_visited': False, 'b_visited': False, 'n_visited': False})
        states.append(new_state)
    return states, agents_list


def build_successors(G, belief):
    while G.graph['modified']:
        G.graph['modified'] = False
        G = build_knowledge_sucessors(G, belief)
        G = build_temporal_sucessors(G, belief)
    return G


def contract(G, belief):
    for node in G:
        if not G.node[node]['contract_visited']:
            for formula in G.node[node]['formulae']:
                if (is_eventually(formula['formula']) or is_until(formula['formula'])) and not is_resolvable(G, node, formula['formula'], belief):
                    G.remove_node(node)
                    G.graph['modified'] = True
                    return G
                if is_next(formula['formula']):
                    has_n_successor = False
                    for successor in G[node]:
                        if G[node][successor][0]['label'] == 'n':
                            has_n_successor = True
                    if not has_n_successor:
                        G.remove_node(node)
                        G.graph['modified'] = True
                        return G
                if is_negated_unary_or_atom(formula['formula'],'knowledge'):
                    label = 'R'+ str(formula['formula'][1][0][1:])
                    has_label_successor = False
                    for successor in G[node]:
                        parsetree_list = sort_recursive(get_NNF_recursive(get_negation(formula['formula'][1][1]))) #inside formula of a negated knowledge formula may not be in NNF
                        if belief:
                            formula_dict = {'formula':parsetree_list, 'k_visited': True, 'b_visited': True, 'n_visited': True} #watch this
                        else:
                            formula_dict = {'formula':parsetree_list, 'k_visited': True, 'b_visited': False, 'n_visited': True} #watch this
                        if G[node][successor][0]['label'] == label and formula_dict in G.node[successor]['formulae']:
                            has_label_successor = True
                    if not has_label_successor:
                        G.remove_node(node)
                        G.graph['modified'] = True
                        return G
                if belief:
                    if is_knowledge(formula['formula']):
                        label = 'R'+ str(formula['formula'][0][1:])
                        has_label_successor = False
                        for successor in G[node]:
                            formula_dict = {'formula':formula['formula'][1], 'k_visited': True, 'b_visited': True, 'n_visited': True} #watch this
                            if G[node][successor][0]['label'] == label and formula_dict in G.node[successor]['formulae']:
                                has_label_successor = True
                        if not has_label_successor:
                            G.remove_node(node)
                            G.graph['modified'] = True
                            return G
    return G



def is_resolvable(G, node, formula, belief):
    if is_eventually(formula):
        check_formula = formula[1]
    else: #is_until
        check_formula = formula[0][3]
    if belief:
        check_formula_dict = {'formula':check_formula, 'k_visited': True, 'b_visited': True, 'n_visited': True}
    else:
        check_formula_dict = {'formula':check_formula, 'k_visited': True, 'b_visited': False, 'n_visited': True}
    return temporal_bfs(G, node, check_formula_dict)


def temporal_bfs(G, node, check_formula_dict):
    queue = deque([])
    visited = set()
    visited.add(node)
    queue.append(node)
    while queue:
        current_node = queue.popleft()
        if check_formula_dict in G.node[current_node]['formulae']:
            return True
        for successor in G[current_node]:
            if G[current_node][successor][0]['label'] == 'n':
                if successor not in visited:
                    visited.add(successor)
                    queue.append(successor)
            else:
                continue
    return False


def build_knowledge_sucessors(G, belief):
    for node in G:
        for formula in G.node[node]['formulae']:
            if not formula['k_visited']:
                formula['k_visited'] = True
                if is_negated_unary_or_atom(formula['formula'],'knowledge'):
                    new_state_formula_list = []
                    idx = str(formula['formula'][1][0][1:]) #index of the knowledge formula
                    G.node[node]['has_negated_k'].append(idx)
                    new_state_formula_list.append(sort_recursive(get_NNF_recursive(get_negation(formula['formula'][1][1])))) #inside formula of a negated knowledge formula may not be in NNF
                    for f in G.node[node]['formulae']:
                        if is_knowledge(f['formula']) and str(f['formula'][0][1:]) == idx and f['formula'] not in new_state_formula_list:
                            new_state_formula_list.append(f['formula'])
                            new_state_formula_list.append(f['formula'][1])
                        if  is_negated_unary_or_atom(f['formula'], 'knowledge') and str(f['formula'][1][0][1:]) == idx and f['formula'] not in new_state_formula_list:
                            new_state_formula_list.append(f['formula'])
                    new_state_pc_tableaux = get_tableaux(new_state_formula_list, belief)
                    if new_state_pc_tableaux:
                        new_states, agents_list = build_states(new_state_pc_tableaux)
                        for state in new_states:
                            if str(state) not in G:
                                G.add_node(str(state), formulae=state, contract_visited=False, has_negated_k=[])
                            if (node,str(state)) not in G.edges():
                                G.add_edge(node,str(state), label='R'+idx)
                        G.graph['modified'] = True
                        return G
        if belief:
            for formula in G.node[node]['formulae']:
                if not formula['b_visited']:
                    formula['b_visited'] = True
                    if is_knowledge(formula['formula']) and str(formula['formula'][0][1]) not in G.node[node]['has_negated_k']:
                        new_state_formula_list = []
                        for f in G.node[node]['formulae']:
                            if is_knowledge(f['formula']) and str(f['formula'][0][1:]) == str(formula['formula'][0][1:]) and f['formula'] not in new_state_formula_list:
                                new_state_formula_list.append(f['formula'])
                                new_state_formula_list.append(f['formula'][1])
                        new_state_pc_tableaux = get_tableaux(new_state_formula_list, belief)
                        if new_state_pc_tableaux:
                            new_states, agents_list = build_states(new_state_pc_tableaux)
                            for state in new_states:
                                if str(state) not in G:
                                    G.add_node(str(state), formulae=state, contract_visited=False, has_negated_k=[])
                                if (node,str(state)) not in G.edges():
                                    G.add_edge(node,str(state), label='R'+str(formula['formula'][0][1:]))
                            G.graph['modified'] = True
                            return G
    return G


def build_temporal_sucessors(G, belief):
    for node in G:
        for formula in G.node[node]['formulae']:
            if not formula['n_visited']:
                formula['n_visited'] = True
                if is_next(formula['formula']):
                    new_state_formula_list = []
                    new_state_formula_list.append(formula['formula'][1])
                    for f in G.node[node]['formulae']:
                        if is_next(f['formula']) and f['formula'][1] not in new_state_formula_list:
                            new_state_formula_list.append(f['formula'][1])
                    new_state_pc_tableaux = get_tableaux(new_state_formula_list, belief)
                    if new_state_pc_tableaux:
                        new_states, agents_list = build_states(new_state_pc_tableaux)
                        for state in new_states:
                            if str(state) not in G:
                                G.add_node(str(state), formulae=state, contract_visited=False, has_negated_k=[])
                            if (node,str(state)) not in G.edges():
                                G.add_edge(node,str(state), label='n')
                        G.graph['modified'] = True
                        return G
    return G


def get_graph(tableaux_list, idx, belief):
    '''
    :param tableaux_list: List list of tableau dict structure with a list of tableau and some global attributes
    :param idx: Int index of the graph
    :param belief: Boolean if it is to use logic of belief
    :return: Dict containing the states list, next time relation list and knowledge relation list
    '''
    if tableaux_list:
        states, agents_list = build_states(tableaux_list)
        MDG = nx.MultiDiGraph(name='Tableau Graph', modified=True, agents_list=agents_list)
        for state in states:
            MDG.add_node(str(state), formulae=state, contract_visited=False, has_negated_k=[])
        MDG = build_successors(MDG, belief)
        MDG.graph['modified'] = True
        draw_graph(MDG, idx)
        while MDG.graph['modified']:
            MDG.graph['modified'] = False
            MDG = contract(MDG,belief)
        #print 'nodes: ' + str(MDG.nodes())
        #print 'edges: ' + str(MDG.edges())
        print nx.info(MDG)
        print 'nodes:'
        for index, node in enumerate(MDG):
            print str(index) + ': ',
            for formula in MDG.node[node]['formulae']:
                print str(formula['formula']) + ',',
            print
        draw_graph(MDG, idx)
    else:
        print 'this tableaux is not proper'


def draw_graph(G, idx):
    '''
    :param G: NetworkX graph
    :return: None
    '''
    G = nx.convert_node_labels_to_integers(G)
    #font = {'fontname'   : 'Perpetua',
    #        'color'      : 'k',
    #        'fontweight' : 'bold',
    #        'fontsize'   : 14}
    #plt.title('Tableau Graph ' + str(idx), font)
    #try:
    #    pos=nx.graphviz_layout(G)
    #except:
    #    pos=nx.spring_layout(G)
    #nx.draw_networkx_nodes(G,pos,node_color='black',alpha=0.4, node_size=500)
    #nx.draw_networkx_edges(G,pos,alpha=0.5,width=1.0)
    #nx.draw_networkx_labels(G, pos, fontsize=14)
    #nx.draw_networkx_edge_labels(G, pos)
    #plt.axis('off')
    #plt.savefig('img/' + str(idx) + '.png')
    aG = nx.to_agraph(G)
    aG.layout(prog='dot')
    #aG.write('img/graphviz_' + str(idx) + '.dot')
    aG.draw('img/graphviz_' + str(idx) + '.png')
