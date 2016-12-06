#! /usr/bin/env python

import random
import re
import sys
import getopt

# TODO: Implement help.
def print_help():
    pass

# Helper for verbose rolls.
def verbose_message(msg, *args):
    if verbose:
        print msg % args


#Return indices of outer parentheses. Raise error if mismatched.
def paren_slice(roll_string, trace=0):
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
    verbose_message("Level %d [paren_slice]:\tSlicing %s from %s", trace,
                   roll_string[idx_left: idx_right+1], roll_string)
    return (idx_left+1,idx_right)


#Roll a string in the form of xdy, i.e. roll x y-sided dice and sum results.
def roll(xdy, trace=0):
    x,y = xdy.split('d')
    x = int(x) if x else 1
    y = int(y)
    roll_result = sum([random.randint(1,y) for d in range(x)])
    verbose_message("Level %d [roll]:\t\tRolling %s: %d", trace, xdy,
                    roll_result)
    return roll_result

# Split a roll string by outer parentheticals.
# Recursivelly evaluate the enclosed substring, then
# substitute xdy substrings with the results of roll.

def eval_roll(roll_string, trace=0):
    verbose_message("Level %d [eval_roll]:\tEvaluating %s", trace,
                    roll_string)
    level = trace+1 if trace else 0
    eval_string = roll_string

    if re.search("^[^\)]*\(.*\)[^\(]*$",eval_string):
        left, right = paren_slice(eval_string, level)
        eval_string = "%s%d%s" % (eval_string[:left-1],
                                  eval_roll(eval_string[left:right], level),
                                  eval_string[right+1:])
        verbose_message("Level %d [eval_roll]:\tCondensed %s to %s", trace,
                        roll_string, eval_string)

    eval_string = re.sub("\d*d\d+", lambda x: str(roll(x.group(), level)),
                         eval_string)

    try:
        roll_result = int(calculate(eval_string))
    except:
        raise ValueError("Malformed Roll String: %s" % roll_string)

    verbose_message("Level %d [eval_roll]:\tCalculated %s as %d", trace,
                    eval_string, roll_result)

    return roll_result


# TODO: Implement so we don't use eval
def op(expr):
    op_dict = {
        '+': lambda a, b: a+b,
        '-': lambda a, b: a-b,
        '/': lambda a, b: a/b,
        '*': lambda a, b: a*b
    }
    pattern = re.compile(r'(\d*\.?\d+)([\+\-\/\*])(\-?\d*\.?\d+)')
    left, op, right = pattern.search(expr).groups()
    left, right = float(left), float(right)
    try:
        operator = op_dict[op]
    except KeyError:
        raise ArgumentError("Operator must be +, -, / or *.")
    return str(operator(left, right))

def calculate(expr):
    pattern_md = re.compile(r'\d*\.?\d+[\*\/]\-?\d*\.?\d+')
    pattern_as = re.compile(r'\d*\.?\d+[\+\-]\-?\d*\.?\d+')
    while pattern_md.search(expr):
      expr = pattern_md.sub(lambda x: op(x.group()), expr)
    while pattern_as.search(expr):
      expr = pattern_as.sub(lambda x: op(x.group()), expr)
    return float(expr)

# For rolling multiple subrolls separately.
def array_roll(args, trace=0):
    verbose_message("Level %d [array_roll]:\tEvaluating %s", trace,
                    ' '.join(args))
    level = trace + 1 if trace else 0
    local_args = list(args)
    roll_value = eval_roll(local_args.pop(0), level)
    # if we've multiple roll strings, we're rolling an array
    if local_args:
        verbose_message("Level %d [array_roll]:\tExpanding to List of size %d",
                        trace, roll_value)
        results = [array_roll(local_args, level) for arg in range(roll_value)]
        if sort_results:
            results.sort()
        return results
    else:
        return roll_value

if __name__ == "__main__":
    arg_list = sys.argv[1:]
    opt_string = "vhs"
    extra=["verbose", "help", "sort"]
    #TODO: Ditch getopts. It trips when handing roll strings beginning
    #with a negative, tries to parse them.
    opts, args = getopt.getopt(arg_list, opt_string, extra)
    verbose = 0
    sort_results = False

    for opt in opts:
        if opt[0] in ['-v', '--verbose']:
            verbose = 1
        elif opt[0] in ['-h', '--help']:
			print_help(); sys.exit(0)
        elif opt[0] in ['-s', '--sort']:
            sort_results = True

    if not(args):
        args = ["d20"]

    dimension = 0
    payload = None

    try:
        print array_roll(args, verbose)
        sys.exit(0)
    except ValueError as ve:
        print ve
        sys.exit(1)
