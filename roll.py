#! /usr/bin/env python
"""
py-roll - Simulate rolling dice from the terminal.
"""

import random
import re
import sys
import getopt

# TODO: Implement help.
def _print_help():
    pass


# Helper for verbose rolls.
def _verbose_message(msg, *msg_params):
    if verbose:
        print msg % msg_params


# Return indices of outer parentheses. Raise error if mismatched.
def _paren_slice(roll_string, trace=0):
    idx_left, idx_right = 0, len(roll_string)-1
    while roll_string[idx_left] != '(':
        idx_left += 1
        if idx_left == len(roll_string):
            break
    while roll_string[idx_right] != ')':
        idx_right -= 1
        if idx_right == 0:
            break
    if idx_left >= idx_right:
        raise ValueError("Mismatched Parentheticals in string '%s'" %\
                         roll_string)
    _verbose_message("Level %d [_paren_slice]:\tSlicing %s from %s", trace,
                     roll_string[idx_left: idx_right+1], roll_string)
    return (idx_left+1, idx_right)


def roll(xdy, trace=0):
    """ Simulates rolling xdy, or x y-sided dice. """
    num_dice, die_size = xdy.split('d')
    num_dice = int(num_dice) if num_dice else 1
    die_size = int(die_size)
    roll_result = [random.randint(1, die_size) for _ in range(num_dice)]
    summed_result = sum(roll_result)
    _verbose_message("Level %d [roll]:\t\tRolling %s: %s => %d", trace, xdy,
                     roll_result, summed_result)
    return summed_result


# Split a roll string by outer parentheticals.
# Recursivelly evaluate the enclosed substring, then
# substitute xdy substrings with the results of roll.

def eval_roll(roll_string, trace=0):
    """ Recursively evaluates a single roll string. """
    _verbose_message("Level %d [eval_roll]:\tEvaluating %s", trace,
                     roll_string)
    level = trace+1 if trace else 0
    eval_string = roll_string

    if re.search(r'^[^\)]*\(.*\)[^\(]*$', eval_string):
        left, right = _paren_slice(eval_string, level)
        eval_string = "%s%d%s" % (eval_string[:left-1],
                                  eval_roll(eval_string[left:right], level),
                                  eval_string[right+1:])
        _verbose_message("Level %d [eval_roll]:\tCondensed %s to %s", trace,
                         roll_string, eval_string)

    eval_string = re.sub(r'\d*d\d+', lambda x: str(roll(x.group(), level)),
                         eval_string)

    try:
        roll_result = int(_calculate(eval_string))
    except:
        raise ValueError("Malformed Roll String: %s" % roll_string)

    _verbose_message("Level %d [eval_roll]:\tCalculated %s as %d", trace,
                     eval_string, roll_result)

    return roll_result


# We roll our own expression evaluator so we don't use the built-in eval()
def _eval_op(expr):
    op_dict = {
        '+': lambda a, b: a+b,
        '-': lambda a, b: a-b,
        '/': lambda a, b: a/b,
        '*': lambda a, b: a*b
    }
    pattern = re.compile(r'(\-?\d*\.?\d+)([\+\-\/\*])(\-?\d*\.?\d+)')
    left, op, right = pattern.search(expr).groups()
    left, right = float(left), float(right)
    try:
        operator = op_dict[op]
    except KeyError:
        raise ValueError("Operator must be +, -, / or *.")
    return str(operator(left, right))


def _calculate(expr):
    pattern_md = re.compile(r'\-?\d*\.?\d+[\*\/]\-?\d*\.?\d+')
    pattern_as = re.compile(r'\-?\d*\.?\d+[\+\-]\-?\d*\.?\d+')
    while pattern_md.search(expr):
        expr = pattern_md.sub(lambda x: _eval_op(x.group()), expr, count=1)
    while pattern_as.search(expr):
        expr = pattern_as.sub(lambda x: _eval_op(x.group()), expr, count=1)
    return float(expr)


# For rolling multiple subrolls separately.
def array_roll(roll_strings, trace=0):
    """
        expands an array of n roll strings into an (n-1) dimensional array of
        roll results
    """
    _verbose_message("Level %d [array_roll]:\tEvaluating %s", trace,
                     ' '.join(roll_strings))
    level = trace + 1 if trace else 0
    local_args = list(roll_strings)
    roll_value = eval_roll(local_args.pop(0), level)

    # if we've multiple roll strings, we're rolling an array

    if local_args:
        _verbose_message("Level %d [array_roll]:\tExpanding to list of size %d",
                         trace, roll_value)
        results = [array_roll(local_args, level) for _ in range(roll_value)]
        if sort_results:
            results.sort()
        return results
    else:
        return roll_value


if __name__ == "__main__":
    NEG_NUM = re.compile(r'^\-[\dd].*$')
    OPT_STRING = "vhs"
    EXTRA = ["verbose", "help", "sort"]

    # Prepend 0 to negative numbers to keep getopts happy.
    args = [
        x if NEG_NUM.match(x) else NEG_NUM.sub(lambda n: "0" + n.group(), x)
        for x in sys.argv[1:]
    ]

    opts, args = getopt.getopt(args, OPT_STRING, EXTRA)

    verbose = 0
    sort_results = False

    for opt in opts:
        if opt[0] in ['-v', '--verbose']:
            verbose = 1
        elif opt[0] in ['-h', '--help']:
            _print_help()
            sys.exit(0)
        elif opt[0] in ['-s', '--sort']:
            sort_results = True

    if not args:
        args = ["d20"]

    try:
        print array_roll(args, verbose)
        sys.exit(0)
    except ValueError as value_error:
        print value_error
        sys.exit(1)
