import unittest

from srcLRparsing import grammar as Grammar
from srcLRparsing import formula_utils as FormulaUtils

__author__ = 'thiagovieira'


class FormulaUtilsTest(unittest.TestCase):
    def setUp(self):
        self.formula_cases = ['p0', 'true', '~~false', 'p0 v p1',
                              'p1 ^ (p2 ^ p3)', 'k1p0', '~~p1 U q5',
                              'k1k2p0',
                              'p0v~Np3', 'Gk2p3 -> true', 'p9->k1Gp9',
                              'G(p9->p0)', '(~~p9vp4)', '~p3 -> (p4 -> Fp3)',
                              '~(~~p9vp4)vFp2',
                              'k3(k2p2v(r1->Gt3))']
        self.prop_cases = ['p0', 'p2']
        self.false_case = ['false']
        self.true_case = ['true']
        self.knowledge_cases = ['k1p3', 'k1k2k3p4', 'k3(k2p2v(r1->Gt3))']
        self.next_cases = ['Nk1p0', 'N(p0 -> p9)']
        self.always_cases = ['Gk1p0', 'G(p0 -> p9)']
        self.eventually_cases = ['Fk1p0', 'F(p0 -> p9)']
        self.negation_cases = ['~k1p0', '~(p0 -> p9)']
        self.unary_cases = ['Nk1p0', 'k1p0', '~k1p0', 'G(p0 -> p9)',
                            'k3(k2p2v(r1->Gt3))']
        self.conjunction_cases = ['k1k2p2 ^ p0', '(p1 v Np3) ^ Gk1p3']
        self.disjunction_cases = ['p1 v p2 ^ p3', 'Np0 v GNp9']
        self.implication_cases = ['p9 -> k1Gp9', '~p9 v p4 -> Fp3',
                                  '~p9 -> p4 -> Fp3']
        self.until_cases = ['p9 U k1Gp9', '~p9 ^ p4 U Fp3']
        self.binary_cases = ['p1 v p2 ^ p3', '(p1 v Np3) ^ Gk1p3',
                             '~p9 ^ p4 -> Fp3', 'p9 U k1Gp9',
                             '(~(~~p9vp4)vFp3)']
        self.atom_cases = ['t8', 'p0', 'true', 'false']

        self.binary_operators = ['v', '^', '->', 'U']
        self.unary_operators = ['~', 'G', 'F', 'N']

    def get_parsetree_list(self, case):
        parse_tree = Grammar.parse_formula(case)
        parse_tree_string = Grammar.get_parsetree_string(parse_tree)
        return FormulaUtils.parsetree_string_to_list(
            parse_tree_string)

    def test_is_unary(self):
        for test in self.unary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_unary(parsetree_list)
            self.assertTrue(result)
        for test in self.binary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_unary(parsetree_list)
            self.assertFalse(result)
        for test in self.atom_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_unary(parsetree_list)
            self.assertFalse(result)

    def test_is_binary(self):
        for test in self.binary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_binary(parsetree_list)
            self.assertTrue(result)
        for test in self.unary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_binary(parsetree_list)
            self.assertFalse(result)
        for test in self.atom_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_binary(parsetree_list)
            self.assertFalse(result)

    def test_is_atom(self):
        for test in self.atom_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_atom(parsetree_list)
            self.assertTrue(result)
        for test in self.binary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_atom(parsetree_list)
            self.assertFalse(result)
        for test in self.unary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_atom(parsetree_list)
            self.assertFalse(result)

    def test_get_main_operator(self):
        for test in self.binary_cases:
            parsetree_list = self.get_parsetree_list(test)
            main_operator = FormulaUtils.get_main_operator(parsetree_list)
            if main_operator in self.binary_operators:
                result = True
            else:
                result = False
            self.assertTrue(result)
        for test in self.unary_cases:
            parsetree_list = self.get_parsetree_list(test)
            main_operator = FormulaUtils.get_main_operator(parsetree_list)
            if (main_operator in self.unary_operators) or (
                        'k' in main_operator):
                result = True
            else:
                result = False
            self.assertTrue(result)

    def test_is_false(self):
        for test in self.false_case:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_false(parsetree_list)
            self.assertTrue(result)
        for test in self.unary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_false(parsetree_list)
            self.assertFalse(result)

    def test_is_true(self):
        for test in self.true_case:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_true(parsetree_list)
            self.assertTrue(result)
        for test in self.unary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_true(parsetree_list)
            self.assertFalse(result)

    def test_is_negation(self):
        for test in self.negation_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_negation(parsetree_list)
            self.assertTrue(result)
        for test in self.binary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_negation(parsetree_list)
            self.assertFalse(result)
        for test in self.eventually_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_negation(parsetree_list)
            self.assertFalse(result)

    def test_is_conjuction(self):
        for test in self.conjunction_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_conjuction(parsetree_list)
            self.assertTrue(result)
        for test in self.unary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_conjuction(parsetree_list)
            self.assertFalse(result)
        for test in self.disjunction_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_conjuction(parsetree_list)
            self.assertFalse(result)

    def test_is_disjunction(self):
        for test in self.disjunction_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_disjunction(parsetree_list)
            self.assertTrue(result)
        for test in self.unary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_disjunction(parsetree_list)
            self.assertFalse(result)
        for test in self.implication_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_disjunction(parsetree_list)
            self.assertFalse(result)

    def test_is_knowledge(self):
        for test in self.knowledge_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_knowledge(parsetree_list)
            self.assertTrue(result)
        for test in self.binary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_knowledge(parsetree_list)
            self.assertFalse(result)
        for test in self.eventually_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_knowledge(parsetree_list)
            self.assertFalse(result)

    def test_is_always(self):
        for test in self.always_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_always(parsetree_list)
            self.assertTrue(result)
        for test in self.binary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_always(parsetree_list)
            self.assertFalse(result)
        for test in self.eventually_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_always(parsetree_list)
            self.assertFalse(result)

    def test_is_eventually(self):
        for test in self.eventually_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_eventually(parsetree_list)
            self.assertTrue(result)
        for test in self.binary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_eventually(parsetree_list)
            self.assertFalse(result)
        for test in self.next_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_eventually(parsetree_list)
            self.assertFalse(result)

    def test_is_next(self):
        for test in self.next_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_next(parsetree_list)
            self.assertTrue(result)
        for test in self.binary_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_next(parsetree_list)
            self.assertFalse(result)
        for test in self.knowledge_cases:
            parsetree_list = self.get_parsetree_list(test)
            result = FormulaUtils.is_next(parsetree_list)
            self.assertFalse(result)


    def test_get_negation(self):
        pass

    def test_is_negated_unary_or_atom(self):
        #TODO
        pass

    def test_lex_sort(self):
        #TODO
        pass

    def test_remove_implications_recursive(self):
        pass

    def test_get_NNF_recursive(self):
        pass

    def test_propagate_negation_binary(self):
        pass

    def test_propagate_negation_unary(self):
        pass


class TableauTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()