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