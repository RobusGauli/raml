#this is the new functionality in python 36

class Contract:
    @classmethod
    def check(cls, val):
        pass
    
    def __set__(self, instance, value):
        self.check(value)
        #only then
        instance.__dict__[self.name] = value
    
    def __set_name__(self, cls, name):
        self.name = name
    


class Type(Contract):
    ty = None
    @classmethod
    def check(cls, val):
        assert isinstance(val, cls.ty), 'Expected {}'.format(cls.ty)
        super().check(val)
class Integer(Type):
    ty = int

class Float(Type):
    ty = float

class String(Type):
    ty = str

class Positive(Contract):
    @classmethod
    def check(cls, val):
        assert val > 0, 'Expected Positive Value'
        super().check(val)

class PositiveInteger(Integer, Positive):
    pass


class PositiveFloat(Float, Positive):
    pass

class NonEmpty(Contract):
    @classmethod
    def check(cls, val):
        assert len(val) >= 1, 'Expecter non empty string'
        super().check(val)

class NonEmptyString(String, NonEmpty):
    pass


def summer(a, b):
    Integer.check(a)
    Integer.check(b)
    return a + b 


#there is a new feature in python 35 called type annotaions

def summer(a: PositiveInteger, b: Integer):
    return a + b


#write a small sully errror prone decorator

from functools import wraps
from inspect import signature

def check(func):
    ann = func.__annotations__
    sig = signature(func)
    @wraps(func)
    def wrapper(*args, **kwargs):
        #here is the code
        bound = sig.bind(*args, **kwargs)
        for key, val in bound.arguments.items():
            if key in ann:
                ann[key].check(val)
        return func(*args, **kwargs)
    return wrapper



@check
def summer(a: PositiveInteger, b: Integer):
    return a + b
@check
def add_string(a: NonEmptyString, b: NonEmptyString):
    return a + b




#i think this is way cooler than writeing the boring old java 


#now lets move to some insane jorney 
class Player:

    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
    
    def move(self, dx):
        self.x += dx

    @property
    def name(self):
        return self.name
    
    @name.setter
    def name(self, val):
        assert len(val) >= 1, 'Expected non empty string'
        self.name = val
    #if i go on writing this nonsense 
    #I will leave the coding 
    #and join the hot dog company

    #naaaaaaaaa

#i will introduce the new concept that the framework builder use 

#that is called descriptor protocol


class Person:
    #can you spot the smell of djanog herer
    name = String()
    age = Integer()
    price = PositiveInteger()

    def __init__(self, name, age, price):
        self.name = name
        self.age = age
        self.price = price
    
    def __repr__(self):
        return 'Person({}, {}, {})'.format(self.name, self.age, self.price)
    
from inspect import Signature
from inspect import Parameter

make_signature = lambda _fields : Signature([Parameter(f, Parameter.POSITIONAL_OR_KEYWORD) for f in _fields])

class MyType(type):

    #metaclass

    def __new__(cls, clsname, bases, clsdict):
        _fields = [key for key, val in clsdict.items() if isinstance(val, Contract)]
        sig = make_signature(_fields)
        clsdict['sig'] = sig
        return super().__new__(cls, clsname, bases, clsdict)


class Base(metaclass=MyType):

    def __init__(self, *args, **kwargs):
        #i will assume i will have signature from somewhere
        bound = self.sig.bind(*args, **kwargs)
        for key, val in bound.arguments.items():
            setattr(self, key, val)
        


class Person(Base):
    #this is looking to similart to django already
    name = String()
    age = Integer()
    price = PositiveFloat()

#can we go further ahead

class Person(Base):
    name: String
    age : Integer
    price: PositiveFloat


#can we ??

class MyType(type):

    def __new__(cls, clsname, bases, clsdict):
        _cls = super().__new__(cls, clsname, bases, clsdict)
        _ann = getattr(_cls, '__annotations__', None)
        #decorating all the shit
        for key, val in _cls.__dict__.items():
            if callable(val):
                setattr(_cls, key, check(val))

        if _ann:
            _fields = list(_ann.keys())
            sig = make_signature(_fields)
            setattr(_cls, 'sig', sig)

            #also we need to create a object of the protocol and set it tot eh class classname(object):

            for key, val in _ann.items():
                v = val()
                v.__set_name__(_cls, key)
                setattr(_cls, key, v)
        return _cls

class Base(metaclass=MyType):
    def __init__(self, *args, **kwargs):
        bound = self.sig.bind(*args, **kwargs)
        for key, val in bound.arguments.items():
            setattr(self, key, val)

class Person(Base):
    name : String
    age : Integer
    price: Float

    #I think this is awesome af

    def move(self, dx: PositiveFloat):
        self.price += dx





