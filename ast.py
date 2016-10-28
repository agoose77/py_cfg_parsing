from collections import namedtuple
from enum import Enum


ArgUnpackTypes = Enum('ArgUnpackTypes', 'args kwargs none')
UnaryOpType = Enum('UnaryOp', 'pos inv neg')
BinOpType = Enum('BinOp', 'add div sub mod pow mult')

Slice = namedtuple('Subscript', 'first second third')

Dict = namedtuple('Dict', 'keys values')
List = namedtuple('List', 'values')
Set = namedtuple('Set', 'elements')
Tuple = namedtuple('Tuple', 'values')
String = namedtuple('String', 'value')
Assignment = namedtuple('Assignment', 'targets value')
FunctionDef = namedtuple('FunctionDef', 'name args body decorators returns')
Pass = namedtuple('Pass', '')
Ellipsis_ = namedtuple('Ellipsis_', '')
None_ = namedtuple('None_', '')
Del = namedtuple('Del', '')
Not = namedtuple('Not', 'expression')
Continue = namedtuple('Continue', '')
Break = namedtuple('Break', '')
Return = namedtuple('Return', 'value')
Nonlocal = namedtuple('Nonlocal', 'names')
Global = namedtuple('Global', 'names')
Raise = namedtuple('Raise', 'exc cause')
LambdaDef = namedtuple('LambdaDef', 'args body')
Comparison = namedtuple('Comparison', 'left op exprs')
IfExp = namedtuple('IfExp', 'test body or_else')
While = namedtuple('While', 'test body or_else')
For = namedtuple('For', 'target iter body or_else')
ClassDef = namedtuple('ClassDef', 'name bases keywords body decorators')
Attribute = namedtuple('Attribute', 'value attr')
Subscript = namedtuple('Subscript', 'value slice')
Call = namedtuple('Call', 'func args keywords')
Arg = namedtuple('Arg', 'name value unpack')
BinOp = namedtuple('BinOp', 'left op right')
UnaryOp = namedtuple('UnaryOp', 'op operand')