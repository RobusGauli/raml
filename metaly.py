import os
import sys
import collections
from collections import namedtuple, defaultdict, Counter, Iterable, Iterator
from collections import deque


class Person:

    def __init__(self, name, age, price):
        self.name = name
        self.age = age
        self.price = price


class Vector:

    def __init__(self, x, y):
        self.x = x
        self.y = y
    

class Share:

    def __init__(self, name, price):
        self.name = name
        self.price = price


class Contract:

    def __set_name__(self, cls, name):
        self.name = name

    def __set__(self, instance, value):
        #print
        print('setting...')
        instance.__dict__[self.name] = value



from inspect import Signature, Parameter

make_signature = lambda _fields : Signature([Parameter(f, Parameter.POSITIONAL_OR_KEYWORD) for f in _fields])


class MyType(type):

    def __new__(cls, clsname, bases, clsdict):
        #get the fields attribute
        _fields = [key for key, val in clsdict.items() if isinstance(val, Contract)]
        if _fields:
            sig = make_signature(_fields)
            clsdict['sig'] = sig
        return super().__new__(cls, clsname, bases, clsdict)

class Base(metaclass=MyType):

    
    def __init__(self, *args, **kwargs):
        bound = self.sig.bind(*args, **kwargs)
        for key, val in bound.arguments.items():
            setattr(self, key, val)
        
        
    
class Person(Base):
    fields = 'name age'.split()

class Vector(Base):
    fields = 'x y'.split()



class Typed(Contract):
    ty = None
    def __set__(self, instance, value):
        assert isinstance(value, self.ty), 'Expected {}'.format(self.ty)
        super().__set__(instance, value)

class String(Typed):
    ty = str

class Integer(Typed):
    ty = int

class Float(Typed):
    ty = float


class Positive(Contract):

    def __init__(self, *args, positive=False, **kwargs):
        self.positive = positive
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if self.positive and value is not None:
            assert value > 0, 'Expected Positive value'
        super().__set__(instance, value)


class NotNull(Contract):

    def __init__(self, *args, notnull=False, **kwargs):
        self.notnull = notnull
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if self.notnull:
            assert value != None,' Value cannot be None'
        super().__set__(instance, value)

class NonEmpty(Contract):

    def __init__(self, *args, empty=True, **kwargs):
        self.empty = empty
        super().__init__(*args, **kwargs)
    
    def __set__(self, instance, value):
        if self.empty == False:
            assert len(value) >= 1, 'String cannot be non empty'
        super().__set__(instance, value)
    
class RInteger(Integer, Positive, NotNull):
    pass

class RString(String, NotNull, NonEmpty):
    pass

class Person(Base):
    name = RString(empty=False, notnull=True)
    age = RInteger(positive=True)
    #this is how django model workd in the darkest corneer


