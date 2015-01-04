import lrparsing
from lrparsing import Prio, Ref, Token, ParseError, TokenError

__author__ = 'thiagovieira'


class FormulaGrammar(lrparsing.Grammar):
    #
    # Tokens
    #
    class T(lrparsing.TokenRegistry):
        bool_true = Token(re='true')
        bool_false = Token(re='false')
        # cte_start = Token(re='start')
        prop = Token(re='[p-s][0-9]*')
        not_op = Token(re='~')
        conjunction_op = Token(re='\^')
        disjunction_op = Token(re='v')
        implication_op = Token(re='->')
        know_op = Token(re='k[0-9]*')
        eventually_op = Token(re='F')
        always_op = Token(re='G')
        next_op = Token(re='N')
        until_op = Token(re='U')
        unless_op = Token(re='W')

    #
    # Grammar rules.
    #


    atom = T.prop | T.bool_true | T.bool_false #| T.cte_start
    formula = Ref('formula')  # Forward reference
    unary = T.not_op >> formula | T.know_op >> formula | \
            T.eventually_op >> formula | T.always_op >> formula | \
            T.next_op >> formula
    binary = Prio(formula << T.conjunction_op << formula,
                  formula << T.disjunction_op << formula,
                  formula << T.implication_op << formula,
                  formula << T.until_op << formula,
                  formula << T.unless_op << formula)
    formula = atom | '(' + unary + ')' | '(' + binary + ')'
    START = formula


def get_parsetree_string(parse_tree):
    '''
    :param parse_tree: Tuple parse tree from grammar.parse_formula
    :return: String parse tree representation as string
    '''
    return FormulaGrammar.repr_parse_tree(parse_tree)


def parse_formula(formula_string):
    '''
    :param formula_string: String formula to be parsed with grammar
    :return: Tuple parse tree
    '''
    try:
        return FormulaGrammar.parse(formula_string)
    except ParseError, LrParsingError:
        print 'Parser Error'
        print LrParsingError
        print '--------------------------'
    except TokenError, LrParsingError:
        print 'Token error'
        print LrParsingError
        print '--------------------------'
