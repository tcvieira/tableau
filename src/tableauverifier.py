#!/usr/local/bin/python

'''
Usage:
  tableauverifier.py parse --file=<formula-file> [--nnf]
  tableauverifier.py pctableau --file=<formula-file> [--per-line] [--verbose] [--belief]
  tableauverifier.py tableau --file=<formula-file> [--prop=<property>] [--per-line] [--verbose] [--belief]
  tableauverifier.py -h | --help
  tableauverifier.py -v | --version

  Tableau Verifier for S5+PTL and KD45+PLTL multimodal logics

Options:
    -h --help  Show this screen.
    -v --version  Show version of the program
    --nnf  Return formula in Negation Normal Form
    --per-line  A separated tableau for each formula in the file
    --verbose  Show formulae for each tableaux branch
    --belief  Change to the logic of Belief instead of Knowledge

Arguments:
   <formula-file>  formula file containing formulae to be used
   <property>  property formula to be verified

'''

from docopt import docopt

import grammar as Grammar
import formula_utils as FormulaUtils
import tableau as Tableau
import graph as Graph
from utils import timewith


__author__ = 'thiagovieira'


def run_parser_cli(formulae_list, nnf):
    for case in formulae_list:
        print 'original string: ',
        print case
        parse_tree = Grammar.parse_formula(case)
        parsetree_string = Grammar.get_parsetree_string(parse_tree)
        parsetree_list = FormulaUtils.parsetree_string_to_list(parsetree_string)
        print 'parsetree list: ',
        print parsetree_list
        if nnf:
            parsetree_list_no_implications = FormulaUtils.remove_implications_recursive(parsetree_list)
            #print 'with no implications: ',
            #print parsetree_list_no_implications
            parsetree_list_nnf = FormulaUtils.get_NNF_recursive(parsetree_list_no_implications)
            print 'NNF: ',
            print parsetree_list_nnf
            print 'formula size: ',
            print str(FormulaUtils.get_len(parsetree_list_nnf)) + ' symbols'
        # print 'new formula string: ',
        # print FormulaUtils.parsetree_list_to_string_with_parentheses(parsetree_list_nnf)
        print '--------------------------'
        print


def run_tableau_cli(formulae_string_list, per_line, verbose, belief):
    timer_all = timewith('overall time...')
    timer_formulae = timewith('preparing formulae...')
    formulae_list = load_formulae_list(formulae_string_list)
    timer_formulae.checkpoint('formulae preparing')
    if per_line:
        for formula in formulae_list:
            single_list = []
            single_list.append(formula)
            print '======================================================'
            print '======================================================'
            timer_tableaux = timewith('building tableaux...')
            tableaux = Tableau.get_tableaux(single_list, belief)
            timer_tableaux.checkpoint('tableaux built')
            print 'original formula: ' + str(formula)
            print '--------------------------'
            print_tableaux(tableaux, verbose)
    else:
        print '======================================================'
        print '======================================================'
        timer_tableaux = timewith('building tableaux...')
        tableaux = Tableau.get_tableaux(formulae_list, belief)
        timer_tableaux.checkpoint('tableaux built')
        print '--------------------------'
        print_tableaux(tableaux, verbose)
    timer_all.checkpoint('overall time (including prints)')


def print_tableaux(tableaux, verbose):
    if tableaux:
        for index, tableau in enumerate(tableaux):
            print 'tableau branch: ' + str(index)
            timer_is_proper = timewith('checking if it is proper...')
            is_proper = Tableau.is_proper(tableau)
            timer_is_proper.checkpoint('is proper checking')
            print 'is proper: ' + str(is_proper)
            if verbose:
                for formula in tableau['formulae']:
                    print formula['formula']
            print str(len(tableau['formulae'])) + ' formulae in this branch'
            print '--------------------------'
    else:
        print 'this tableaux is not proper'


def run_graph_cli(formulae_string_list, per_line, verbose, belief):
    timer_all = timewith('overall time...')
    formulae_list = load_formulae_list(formulae_string_list)
    if per_line:
        for idx, formula in enumerate(formulae_list):
            single_list = []
            single_list.append(formula)
            print '======================================================'
            print '======================================================'
            tableaux = Tableau.get_tableaux(single_list, belief)
            timer_graph = timewith('building graph...')
            Graph.get_graph(tableaux, idx, belief)
            timer_graph.checkpoint('graph built')
    else:
        print '======================================================'
        print '======================================================'
        tableaux = Tableau.get_tableaux(formulae_list, belief)
        timer_graph = timewith('building graph...')
        Graph.get_graph(tableaux, 0, belief)
        timer_graph.checkpoint('graph built')
    timer_all.checkpoint('overall time (including prints)')


def load_formulae_list(formulae_string_list):
    formulae_list = []
    for case in formulae_string_list:
        parse_tree = Grammar.parse_formula(case)
        parsetree_string = Grammar.get_parsetree_string(parse_tree)
        parsetree_list = FormulaUtils.parsetree_string_to_list(parsetree_string)
        parsetree_list_no_implications = FormulaUtils.remove_implications_recursive(parsetree_list)
        parsetree_list_nnf = FormulaUtils.get_NNF_recursive(parsetree_list_no_implications)
        parsetree_list_sorted = FormulaUtils.sort_recursive(parsetree_list_nnf)
        formulae_list.append(parsetree_list_sorted)
    return formulae_list


def load_from_file(file_name):
    formulae_list = []
    with open(file_name, 'r') as f:
        for line in f.readlines():
            if line[0] != '#':
                formulae_list.append(line)
    f.close()
    return formulae_list


if __name__ == '__main__':
    args = docopt(__doc__, version='S5+PTL Tableau Verifier 0.1', options_first=False)
    formulae_list = load_from_file(args['--file'])
    if args['parse']:
        if args['--nnf']:
            run_parser_cli(formulae_list, True)
        else:
            run_parser_cli(formulae_list, False)
    elif args['pctableau']:
        run_tableau_cli(formulae_list, args['--per-line'], args['--verbose'], args['--belief'])
    elif args['tableau']:
        #TODO: deal with property
        run_graph_cli(formulae_list, args['--per-line'], args['--verbose'], args['--belief'])
    else:
        print 'not implemented'
