# mathexp.py - Python module to parse and evaluate mathematical expressions.
#
# Copyright (C) 2015 Jorge Jonathan Moreno Zúñiga
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
# in a product, an acknowledgment in the product documentation would be
# appreciated but is not required.
#
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
#
# 3. This notice may not be removed or altered from any source distribution.

"""Python module to evaluate mathematical expressions"""
import math

MALFORMED_EXPRESSION_ERROR = "Malformed expression"
EXPRESSION_PARSING_ERROR = "Expression parser error"
SYMBOL_NOT_FOUND_ERROR = "Symbol not found"

MATHEXP_LITERAL = 0
MATHEXP_FUNCTION = 1
MATHEXP_OPERATOR = 2

TOKEN_TYPE_STRING = [
    "MATHEXP_LITERAL",
    "MATHEXP_FUNCTION",
    "MATHEXP_OPERATOR"
]

def fact(num):
    """Simple factorial function as I didn't find a native one in Python"""
    if num % 1 != 0 or num < 0:
        raise Exception("Factorial: Number must be a positive integer")
    num = int(num)
    if num == 0 or num == 1:
        return 1
    res = 1
    for i in range(1, num + 1):
        res *= i
    return res

FUNCTION_LIST = {
    "sin"  : math.sin,
    "cos"  : math.cos,
    "tan"  : math.tan,
    "asin" : math.asin,
    "acos" : math.acos,
    "atan" : math.atan,
    "ln"   : math.log,
    "log"  : math.log10,
    "abs"  : abs,
    "fact" : fact
}


def get_function(exp):
    """Checks if the expression first operation should be a function"""
    for function in FUNCTION_LIST.keys():
        if exp.startswith(function + "(") and exp.endswith(")"):
            exp = exp[len(function)+1:-1]
            if parens_are_balanced(exp):
                return function
    return None

OPERATOR_PRIORITY = {
    "^": -1,
    "*": -2,
    "/": -2,
    "+": -3,
    "-": -3
}


def remove_extra_parens(exp):
    """Checks if there are unneeded extra pairs of parentheses and
    removes them."""
    while exp.startswith("(") and exp.endswith(")") and\
            parens_are_balanced(exp[1:-1]):
        exp = exp[1:-1]
    return exp


def parens_are_balanced(exp):
    """Checks for any imbalance in parentheses"""
    i = 0
    for char in exp:
        if char == "(":
            i += 1
        if char == ")":
            i -= 1
        if i < 0:
            return False
    return i == 0


def evaluate_operator(token, arg1, arg2):
    if token == "^":
        return arg1 ** arg2
    if token == "*":
        return arg1 * arg2
    if token == "/":
        return arg1 / arg2
    if token == "+":
        return arg1 + arg2
    if token == "-":
        return arg1 - arg2
    raise Exception(EXPRESSION_PARSING_ERROR)


def is_operator(token):
    return token in ['^', '*', '/', '+', '-']


def exp_check(exp):
    if not parens_are_balanced(exp):
        raise Exception(MALFORMED_EXPRESSION_ERROR)
    exp = exp.replace(" ", "")
    exp = remove_extra_parens(exp)
    first = exp[0]
    last = exp[-1]
    if is_operator(first) and first != "+" and first != "-":
        raise Exception(MALFORMED_EXPRESSION_ERROR)
    if is_operator(last):
        raise Exception(MALFORMED_EXPRESSION_ERROR)
    if exp[0] == "-":   #Don't know how to overload the - sign operator
        exp = "0" + exp #So just make it a substract from 0
    if exp[0] == "+":
        exp = exp[1:]
    return exp


def is_number(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def lookup_top_operator(exp):
    pos = -1
    level = 0
    i = -1
    for token in exp:
        i += 1
        if token == "(":
            level += 1
            continue
        if token == ")":
            level -= 1
            continue
        if not is_operator(token):
            continue
        if level != 0:
            continue
        if i == 0 or i == len(exp) - 1:
            continue
        if (token == "+" or token == "-") and is_operator(exp[i - 1]):
            continue
        if pos == -1:
            pos = i
            continue
        if OPERATOR_PRIORITY[token] <= OPERATOR_PRIORITY[exp[pos]]:
            pos = i
    return pos


class MathExp:
    """Expression parser class"""
    def __init__(self, exp):
        """The mathematical expression must be a string, and always must be part
        of the constructor."""
        self.variables_table = {}
        exp = exp_check(exp)
        function = get_function(exp)
        if function is not None:
            self.token = function
            self.left = None
            arg = exp[len(self.token)+1:-1]
            self.right = MathExp(arg)
            self.typ = MATHEXP_FUNCTION
            return
        top_operator_pos = lookup_top_operator(exp)
        if top_operator_pos >= 0:
            self.token = exp[top_operator_pos]
            self.typ = MATHEXP_OPERATOR
            exp_izq = exp[:top_operator_pos]
            exp_der = exp[top_operator_pos + 1:]
            self.left = MathExp(exp_izq)
            self.right = MathExp(exp_der)
            return
        self.token = exp
        self.typ = MATHEXP_LITERAL
        self.left = None
        self.right = None

    def evaluate(self, tmp_variables_table=None):
        """tmp_variables_table is a dict containing str : floar pairs, and overrides
        the object's own variable table"""
        if tmp_variables_table is None:
            tmp_variables_table = self.variables_table
        if self.typ == MATHEXP_LITERAL:
            if is_number(self.token):
                res = float(self.token)
                return res
            if self.token not in tmp_variables_table:
                raise Exception(SYMBOL_NOT_FOUND_ERROR + ": " + self.token)
            res = float(tmp_variables_table[self.token])
            return res
        if self.typ == MATHEXP_FUNCTION:
            arg = self.right.evaluate(tmp_variables_table)
            res = FUNCTION_LIST[self.token](arg)
            return res
        if self.typ == MATHEXP_OPERATOR:
            left_value = self.left.evaluate(tmp_variables_table)
            right_value = self.right.evaluate(tmp_variables_table)
            res = evaluate_operator(self.token, left_value, right_value)
            return res
        raise Exception(EXPRESSION_PARSING_ERROR)

    def add_variable(self, key, value):
        self.variables_table[key] = value

    def remove_variable(self, key):
        self.variables_table.pop(key)

    def get_variable(self, key):
        return self.variables_table[key]

    def get_variables_table(self):
        return self.variables_table

    def set_variables_table(self, tmp_variables_table):
        self.variables_table = tmp_variables_table
