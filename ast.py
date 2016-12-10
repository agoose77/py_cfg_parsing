from abc import ABC, abstractmethod
from collections import deque, OrderedDict
from enum import Enum
from functools import partial
from io import StringIO


class AstNode(ABC):

    @abstractmethod
    def _as_dict(self):
        pass

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return False

        try:
            return self._as_dict() == other._as_dict()

        except AttributeError:
            return False


def make_ast_node(name, field_str='', parent=None):
    fields = [f.strip() for f in field_str.split(' ') if f.strip()]
    cls_dict = {}

    if parent is None:
        bases = AstNode,
    else:
        bases = parent, AstNode

    if fields:
        body = "\n    ".join("self.{0} = {0}".format(name) for name in fields)
        field_args = ", ".join(fields)
        declare_init = "def __init__(self, {field_args}):\n    {body}"\
            .format(field_args=field_args, body=body)
        exec(declare_init, cls_dict)

        dict_str = ", ".join("({0!r}, self.{0})".format(name) for name in fields)
        declare_as_dict = "def _as_dict(self):\n    return OrderedDict([{fields}])".format(fields=dict_str)
        exec(declare_as_dict, globals(), cls_dict)

        values_str = ", ".join("self.{0}".format(name) for name in fields)
        declare_hash ="def __hash__(self):\n    return hash(tuple(({values_str},)))".format(values_str=values_str)
        exec(declare_hash, cls_dict)

        formatter_str = ", ".join("self.{}".format(name) for name in fields)
        dict_str = ", ".join("{}={{!r}}".format(name, getattr) for name in fields)
        declare_repr ="def __repr__(self):\n    return '{}({})'.format({})".format(name, dict_str, formatter_str)
        exec(declare_repr, cls_dict)

    else:
        def as_dict(self):
            return {}
        cls_dict['_as_dict'] = as_dict

        def __hash__(self):
            return hash(())
        cls_dict['__hash__'] = __hash__

        declare_repr = "def __repr__(self):\n    return '{}()'".format(name)
        exec(declare_repr, cls_dict)

    print(declare_repr)

    return type(name, bases, cls_dict)


Module = make_ast_node('Module', 'body')
Interactive = make_ast_node('Interactive', 'body')
Expression = make_ast_node('Expression', 'body')

### Statements ##############################################
ClassDef = make_ast_node('ClassDef', 'name bases keywords body decorators')
FuncDef = make_ast_node('FuncDef', 'name args body decorators returns')
Return = make_ast_node('Return', 'value')

Delete = make_ast_node('Delete', 'targets')
Assign = make_ast_node('Assign', 'targets value')
AugAssign = make_ast_node('Augassign', 'target op value')

For = make_ast_node('For', 'target iter body or_else')
While = make_ast_node('While', 'test body or_else')
If = make_ast_node('If', 'test body or_else')
With = make_ast_node('With', 'items body')

Raise = make_ast_node('Raise', 'exc cause')
Try = make_ast_node('Try', 'body handlers orelse finalbody')
Assert = make_ast_node('Assert', 'test msg')

Import = make_ast_node('Import', 'names')
ImportFrom = make_ast_node('ImportFrom', 'module names level')

Global = make_ast_node('Global', 'names')
Nonlocal = make_ast_node('Nonlocal', 'names')
Expr = make_ast_node('Expr', 'exp')
Pass = make_ast_node('Pass', '')
Break = make_ast_node('Break', '')
Continue = make_ast_node('Continue', '')
#############################################################

### Expressions #############################################
BoolOp = make_ast_node('BoolOp', 'values')
BinOp = make_ast_node('BinOp', 'left op right')
UnaryOp = make_ast_node('UnaryOp', 'op operand')
LambdaDef = make_ast_node('LambdaDef', 'args body')
IfExp = make_ast_node('IfExp', 'test body or_else')
Dict = make_ast_node('Dict', 'keys values')
Set = make_ast_node('Set', 'elts')
ListComp = make_ast_node('ListComp', 'elt generators')
SetComp = make_ast_node('SetComp', 'elt generators')
DictComp = make_ast_node('DictComp', 'key value generators')
GeneratorExp = make_ast_node('GeneratorExp', 'elt generators')
# the grammar constrains where yield expressions can occur
Yield = make_ast_node('Yield', 'expr')
YieldFrom = make_ast_node('YieldFrom', 'expr')
# need sequences for compare to distinguish between
# x < 4 < 3 and (x < 4) < 3
Compare = make_ast_node('Compare', 'left ops comparators')
Call = make_ast_node('Call', 'func args keywords')
Num = make_ast_node('Num', 'value')
Str = make_ast_node('Str', 's')
Bytes = make_ast_node('Bytes', 's')
NameConstant = make_ast_node('NameConstant', 'value')
Ellipsis_ = make_ast_node('Ellipsis_', '')

# the following expression can appear in assignment context
Attribute = make_ast_node('Attribute', 'value attr')
Subscript = make_ast_node('Subscript', 'value slice')
Starred = make_ast_node('Starred', 'value')
Name = make_ast_node('Name', 'id')
List = make_ast_node('List', 'values')
Tuple = make_ast_node('Tuple', 'elts')
#############################################################

### Slices ##################################################
Slice = make_ast_node('Subscript', 'first second third')
ExtSlice = make_ast_node('ExitSubscript', 'dims')
Index = make_ast_node('Index', 'value')
#############################################################

# TODO ast inheritance

class OperatorNode(AstNode):
    pass

ArgUnpackTypes = Enum('ArgUnpackTypes', 'args kwargs none')
UnaryOpType = Enum('UnaryOp', 'UAdd Invert USub Not')
BoolOpType = Enum('BoolOp', 'And Or')

OperatorType = Enum('Operator', 'Add Div Sub Mod Pow Mult MatMult RShift LShift BitOr BitXOr BitAnd FloorDiv')
Add = make_ast_node('Add', parent=OperatorNode)
Div = make_ast_node('Div', parent=OperatorNode)
Sub = make_ast_node('Sub', parent=OperatorNode)
Mod = make_ast_node('Mod', parent=OperatorNode)
Pow = make_ast_node('Pow', parent=OperatorNode)
Mult = make_ast_node('Mult', parent=OperatorNode)
MatMult = make_ast_node('MatMult', parent=OperatorNode)
RShift = make_ast_node('RShift', parent=OperatorNode)
LShift = make_ast_node('LShift', parent=OperatorNode)
BitOr = make_ast_node('BitOr', parent=OperatorNode)
BitXOr = make_ast_node('BitXOr', parent=OperatorNode)
BitAnd = make_ast_node('BitAnd', parent=OperatorNode)
FloorDiv = make_ast_node('FloorDiv', parent=OperatorNode)

ComparisonOpType = Enum('ComparisonOp', 'Eq NotEq Lt LtE Gt GtE Is IsNot In NotIn')

Comprehension = make_ast_node('Comprehension', 'target iter ifs')
ExceptionHandler = make_ast_node('ExceptionHandler', 'type name body')

Arguments = make_ast_node('Arguments', 'args vararg kwonlyargs kw_defaults kwarg defaults')
Arg = make_ast_node('Arg', 'arg annotation')

Keyword = make_ast_node('Keyword', 'arg value')# arg=None for **kwargs
Alias = make_ast_node('Alias', 'name asname')
WithItem = make_ast_node('WithItem', 'context_expr optional_vars')

CompFor = make_ast_node('CompFor', 'exprs or_test iterable')
CompIf = make_ast_node('CompIf', 'cond opt')
ImportFromModule = make_ast_node('ImportFromModule', 'level module')
ImportFromSubModules = make_ast_node('ImportFromSubModules', 'aliases')


def red(text):
    return '\x1b[0;31;m' + text


def blue(text):
    return '\x1b[0;34;m' + text


def green(text):
    return '\x1b[0;32;m' + text


def white(text):
    return '\33[0;37;m' + text


colours = red, blue, green, white


def cyclic_colour_formatter(node, level, text):
    colour_f = colours[level % len(colours)]
    return colour_f(text)


def highlight_node_formatter(node_cls, match_format, other_format):
    def wrapper(node, level, text):
        if isinstance(node, node_cls):
            return match_format(text)
        return other_format(text)
    return wrapper


def write_ast(node, writer, level=0, indent='  ', format_func=None):
    if format_func:
        def write(text):
            writer.write(format_func(node, level, text))

    else:
        write = writer.write

    root_margin = indent * level

    as_dict = node._as_dict()

    field_margin = (level + 1) * indent

    if not as_dict:
        write("{}()".format(node.__class__.__name__))

    else:
        write("{}(\n".format(node.__class__.__name__))

        for i, (name, value) in enumerate(as_dict.items()):
            # Between items separate with comma and newline
            if i != 0:
                write(",\n")

            # Write AstNode
            if isinstance(value, AstNode):
                field_text_left = field_margin + "{} = ".format(name)
                write(field_text_left)
                write_ast(value, writer, level + 1, indent, format_func)

            # Write tuple field
            elif type(value) is tuple:
                field_text_left = field_margin + "{} = (\n".format(name)
                write(field_text_left)

                j = -1
                elem_margin = (level + 2) * indent
                for j, elem in enumerate(value):
                    if j != 0:
                        write(",\n")

                    if isinstance(elem, AstNode):
                        write(elem_margin)
                        write_ast(elem, writer, level + 2, indent, format_func)

                    else:
                        write(elem_margin + repr(value))

                if j > -1:
                    write(",\n")
                    write(field_margin + ")")

                else:
                    write(field_margin+")")

            # Write repr
            else:
                write(field_margin + "{} = {!r}".format(name, value))

        write("\n"+root_margin+")")


def iter_fields(node):
    for key, value in node._as_dict().items():
        yield key, value


def iter_child_nodes(node):
    for key in node._fields:
        value = getattr(node, key)

        if isinstance(value, AstNode):
            yield value

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, AstNode):
                    yield item


def walk(node):
    todo = deque([node])
    while todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        yield node


class NodeVisitor:

    def generic_visit(self, node):
        for child in iter_child_nodes(node):
            self.visit(child)

    def visit(self, node):
        visitor_name = "visit_{}".format(node.__class__.__name__)
        visitor = getattr(self, visitor_name, self.generic_visit)
        visitor(node)


class NodeTransformer(NodeVisitor):

    def generic_visit(self, node):
        for field, old_value in iter_fields(node):
            if isinstance(old_value, list):
                new_values = []

                for value in old_value:
                    if isinstance(value, AstNode):
                        value = self.visit(value)
                        if value is None:
                            continue

                        elif not isinstance(value, AstNode):
                            new_values.extend(value)
                            continue

                    new_values.append(value)
                old_value[:] = new_values

            elif isinstance(old_value, AstNode):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)

                else:
                    setattr(node, field, new_node)

        return node


def print_ast(node, format_func=None):
    io = StringIO()
    write_ast(node, io, format_func=format_func)
    print(io.getvalue())
