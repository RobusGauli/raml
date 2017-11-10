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


class Contract:

    def __set_name__(self, cls, name):
        self.name = name

    def __set__(self, instance, value):
        #print
        print('setting...')
        instance.__dict__[self.name] = value


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


class Person(Base):
    
    name = String()
    age = Integer()

class Vector(Base):
    x = Integer()
    y = Integer()
    #this is how django model works out of box