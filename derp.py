from collections import namedtuple
from itertools import product
from abc import ABC, abstractmethod
from functools import wraps

inf = float("+inf")


def memo(f):
    cache = {}

    @wraps(f)
    def f_memo(*args):
        try:
            return cache[args]

        except KeyError:
            result = cache[args] = f(*args)
            return result

    return f_memo


memo_property = lambda f: property(memo(f))


class Undefined:
    pass


def lazy(f, *args, **kwargs):
    value = Undefined

    class proxy:
        def __hash__(self):
            return id(self)

        def __eq__(self, other):
            return id(self) == id(other)

        def __getattr__(self, name):
            nonlocal value
            if value is Undefined:
                value = f(*args, **kwargs)

            return getattr(value, name)

    return proxy()


def record(*fields):
    def decorator(cls):
        cls_dict = {}
        cls_dict['__slots__'] = tuple(fields)

        assert all(f.isidentifier() for f in fields)
        if fields:
            arg_string = ", ".join(fields)
            body_definitions = ["self.{0} = {0}".format(f) for f in fields]
            definition = "def __init__(self, {}):\n\t".format(arg_string) + "\n\t".join(body_definitions)
            exec(definition, cls_dict)

        cls_name = cls.__name__ + "_record"
        return type(cls_name, (cls,), cls_dict)

    return decorator


@record('first', 'second')
class Token:
    pass


class Infix:

    _concat = None
    _alt = None
    _rep = None
    _optional = None
    _reduce = None

    def __and__(self, other):
        return self._concat(self, other)

    def __or__(self, other):
        return self._alt(self, other)

    def __pos__(self):
        return self._rep(self)

    def __invert__(self):
        return self._optional(self)

    def __rshift__(self, other):
        return self._reduce(self, other)


class BaseParser(Infix, ABC):

    @abstractmethod
    def derive(self, token):
        pass

    @abstractmethod
    def derive_null(self):
        pass


class Delayable(BaseParser):

    _null_set = None

    @record('parser', 'token')
    class Delayed(BaseParser):

        @memo_property
        def derivative(self):
            return self.parser._derive(self.token)

        def derive(self, token):
            return self.derivative.derive(token)

        def derive_null(self):
            return self.derivative.derive_null()

    @abstractmethod
    def _derive(self, token):
        pass

    @abstractmethod
    def _derive_null(self):
        pass

    @memo
    def derive(self, token):
        return self.__class__.Delayed(self, token)

    @memo
    def derive_null(self):
        if self._null_set is not None:
            return self._null_set

        new_set = set()

        while True:
            self._null_set = new_set
            new_set = self._derive_null()

            if self._null_set == new_set:
                return self._null_set


@record('value')
class Epsilon(BaseParser):

    def derive(self, token):
        return empty

    def derive_null(self):
        return {self.value}


@record()
class Empty(BaseParser):

    def derive(self, token):
        return empty

    def derive_null(self):
        return set()


@record('string')
class Ter(BaseParser):

    def derive(self, token):
        return Epsilon(token.second) if token.first == self.string else empty

    def derive_null(self):
        return set()


@record('parser')
class Delta(Infix):

    def derive(self, token):
        return empty

    def derive_null(self):
        return self.parser.derive_null()


class Recurrence(Delayable):
    parser = None

    def _derive(self, token):
        return self.parser.derive(token)

    def _derive_null(self):
        return self.parser.derive_null()


# Alt-Concat-Rec
@record('left', 'right')
class Alternate(Delayable):

    def _derive(self, token):
        return Alternate(self.left.derive(token), self.right.derive(token))

    def _derive_null(self):
        deriv_left = self.left.derive_null()
        deriv_right = self.right.derive_null()

        return deriv_left | deriv_right


@record('left', 'right')
class Concatenate(Delayable):
    def _derive(self, token):
        return Alternate(Concatenate(self.left.derive(token), self.right),
                         Concatenate(Delta(self.left), self.right.derive(token)))

    def _derive_null(self):
        result = set()

        deriv_left = self.left.derive_null()
        deriv_right = self.right.derive_null()

        for a, b in product(deriv_left, deriv_right):
            result.add((a, b))

        return result


@record('parser', 'func')
class Reduce(Delayable):

    def _derive(self, token):
        return Reduce(self.parser.derive(token), self.func)

    def _derive_null(self):
        result = set()
        for obj in self.parser.derive_null():
            result.add(self.func(obj))
        return result


def repeat(parser):
    r = Recurrence()
    r.parser = Alternate(epsilon, Concatenate(r, parser))
    return r


def optional(parser):
    return Alternate(epsilon, parser)



Infix._concat = Concatenate
Infix._alt = Alternate
Infix._rep = staticmethod(repeat)
Infix._reduce = Reduce
Infix._optional = staticmethod(optional)


epsilon = Epsilon('')
empty = Empty()


def ter(word):
    return Ter(word)


def parse(parser, tokens):
    for token in tokens:
        parser = parser.derive(token)

    return parser.derive_null()


# examples
if __name__ == '__main__' and 1:
    # S = Recurrence()
    # a = epsilon | (S & ter('1'))
    # S.parser = a
    a = +ter('1')

    print(parse(a, [Token(t, str(i)) for i, t in enumerate(['1', '1', '1'])]))
