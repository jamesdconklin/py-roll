# py-roll
Simple but expressive python script for rolling dice.

## Installation

Mark roll.py as executable, rename as desired, and drop it somewhere within your shell's PATH. However, please read through the file and play around with it elsewhere first. 

## Usage. 

Without arguments, roll.py will roll a d20.

```
jconk@last-ditch:~$ roll
7
```

You can see this more clearly by setting the verbose flag with `-v` or `--verbose`

```
jconk@last-ditch:~$ roll -v
Level 1 [array_roll]:	Evaluating d20
Level 2 [eval_roll]:	Evaluating d20
Level 3 [roll]:		Rolling d20: [6] => 6
Level 2 [eval_roll]:	Calculated 6 as 6
6
```
You can specify different dice or numbers of dice with an xdy format, with integers x and y, where x defaults to 1 if unspecified.

```
jconk@last-ditch:~$ roll 3d6
8
```

Individual roll strings may roll specify simple arithmetic operations to be cocnducted on numeric literals or the results of xdy rolls. 

```
jconk@last-ditch:~$ roll -v 1.5*3d6+2d8/2
Level 1 [array_roll]:	Evaluating 1.5*3d6+2d8/2
Level 2 [eval_roll]:	Evaluating 1.5*3d6+2d8/2
Level 3 [roll]:		Rolling 3d6: [6, 2, 3] => 11
Level 3 [roll]:		Rolling 2d8: [3, 2] => 5
Level 2 [eval_roll]:	Calculated 1.5*11+5/2 as 19
19
```

Some keen-eyed DnD geeks out there might notice that the rounding seems fishy above. The script does not round down until it spits out a final answer to any given roll. 

Parentheses are also supported, but you will need to escape parentheticals or enclose arguments in quotes to prevent your shell from intercepting them. 

```
jconk@last-ditch:~$ roll (2d6+7)/2
bash: syntax error near unexpected token `2d6+7'
jconk@last-ditch:~$ roll "(2d6+7)/2"
7
jconk@last-ditch:~$ roll \(2d6+7\)/2
5
```

If you provide multiple roll strings as arguments, the results will expand into an array with dimension equal to the number of extra roll strings.

```
jconk@last-ditch:~$ roll 6 2d6+6
[11, 14, 14, 14, 17, 13]
```
Nested die rolls, are evaluated once per cycle, even if they govern the size of contained arrays. 

```
jconk@last-ditch:~$ roll 2 d4 2d6+1
[[10, 4], [7, 7, 5, 9]]
```

