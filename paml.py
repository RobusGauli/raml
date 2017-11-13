a = '''

(   
    #kings: [3,4,5,6,(#inner: [jb, cv], #next: cover)],
    #name: robus,
    #age : 1,
    #fitness: (
        #love: sadf,
        #life: 12
    ),
    #asd: life
    
)
'''

b = '''
    (
        #love: there is nothign that hurts more,
        #kindless : there is watcin means,
        #lover: beather
    )
'''

from node import (
    JsonObjectNode,
    AssignmentNode,
    EmptyNode,
    KeyStringNode,
    ValueStringNode,
    JsonListNode
)

LPAREN, RPAREN = 'LPAREN', 'RPAREN'
HASH = 'HASH'
LSBRACKET, RSBRACKET = 'LSBRACKET', 'RSBRACKET'
KEYSTRING = 'KEYSTRING'
VALUESTRING = 'VALUESTRING'
COMMA = 'COMMA'
COLON = 'COLON'
EOF = 'EOF'

class Token:

    def __init__(self, _type, value=None):
        self.type = _type
        self.value = value
    
    def __repr__(self):
        return 'Token({}, {})'.format(self.type, self.value)

lparen_token = lambda: Token(LPAREN)
rparen_token = lambda: Token(RPAREN)
hash_token = lambda: Token(HASH)
lsbracket_token = lambda: Token(LSBRACKET)
rsbracket_token = lambda: Token(RSBRACKET)
#this is the most a
keystring_token = lambda val: Token(KEYSTRING, val)
valuestring_token = lambda val: Token(VALUESTRING, val)

comma_token = lambda: Token(COMMA)
colon_token = lambda: Token(COLON)

eof_token = lambda: Token(EOF)
class Lexer:

    def __init__(self, text):
        self.text = text
        self.current_position = 0
    
    @property
    def current_character(self):
        if self.current_position >= len(self.text):
            return None
        return self.text[self.current_position]
    
    def error(self):
        raise Exception('Token Error')
    

    def skipspace(self):
        #current chatarcter
        while self.current_character is not None and self.current_character.isspace():
            self.advance()
    
    def advance(self):
        self.current_position += 1
    
    def string(self):
        _result = ''
        while self.current_character is not None and self.current_character.isalnum():
            _result += self.current_character
            self.advance()
        return _result
    
    def value_string(self):
        _result = ''
        while self.current_character is not None and (self.current_character.isalnum() or self.current_character.isspace()):
            _result += self.current_character
            self.advance()
        return _result

    

    def get_next_token(self):
        while True:
            if self.current_character is None:
                return eof_token()
                
        
            if self.current_character.isspace():
                self.skipspace()
                continue
            if self.current_character == '(':
                self.advance()
                return lparen_token()
            if self.current_character == ')':
                self.advance()
                return rparen_token()
            if self.current_character == ':':
                self.advance()
                return colon_token()
            if self.current_character == '#':
                #it means there is a key string to be returned
                self.advance()
                return keystring_token(self.string())
            
            if self.current_character == ',':
                self.advance()
                return comma_token()
            
            if self.current_character == '[':
                self.advance()
                return lsbracket_token()

            if self.current_character == ']':
                self.advance()
                return rsbracket_token()

            if self.current_character.isalnum():
                return valuestring_token(self.value_string())

            self.error()


class Parser:
    '''
    Grammar: 
        json_object: (statement)*  ##zero or more statment
                        
        statement: assignment_statement
                    | empty
        assignment_statement: KEYSTRING COLON expr
        expr: factor | LSBRACKET ((COMMA factor)* RSBRACKET 
        factor: VALUESTRING
                | json_object
        
    '''

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    

    def error(self):
        raise Exception('Syntax error')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
    

    def json_object(self):
        _json_object_node = JsonObjectNode()
        if self.current_token.type == LPAREN:
            self.eat(LPAREN)
            #we expect zero or more KEY STRING
            while self.current_token.type == KEYSTRING:
                _statement_node = self.statement()
                _json_object_node.nodes.append(_statement_node)
                
            self.eat(RPAREN)
            return _json_object_node
    
    
    def statement(self):
        #we have the current node as a key string
        return self.assignment_statement()

    def assignment_statement(self):
        #here we have a key string as the current token
        key_string_token = self.current_token
        self.eat(KEYSTRING)
        _colon = self.current_token
        self.eat(COLON)
        #now we have expr
        _node = AssignmentNode(key_string_token, self.expr(), _colon)
        if self.current_token.type == COMMA:
            self.eat(COMMA)
        return _node
    
    def expr(self):

        #here we have simple value string or some
        if self.current_token.type == LSBRACKET:
            #there we are at the list
            self.eat(LSBRACKET)
            _json_list_node = JsonListNode()
            while True:
                if self.current_token.type == RSBRACKET:
                    break
                _json_list_node.nodes.append(self.factor())
                if self.current_token.type == COMMA:
                    self.eat(COMMA)
            self.eat(RSBRACKET)
            self.eat(COMMA)
            return _json_list_node
        return self.factor()
    


    def factor(self):
        #current token is left string or right string
        if self.current_token.type == VALUESTRING:
            _token = self.current_token
            self.eat(VALUESTRING)
            return ValueStringNode(_token)
        if self.current_token.type == LPAREN:
            return self.json_object()

    
    parse = lambda self: self.json_object()


class Interpreter:

    def __init__(self, parser):
        self.parser = parser
    

    def evaluate(self, ast):
        #do the method dispatching
        method_name = 'evaluate_' + type(ast).__name__
        return getattr(self, method_name)(ast)

    def evaluate_JsonObjectNode(self, object_node):
        #make the dictionary out of the object node
        _result = {}
        for assignment_node in object_node.nodes:
            _result[assignment_node.left.value] = self.evaluate(assignment_node.right)
        return _result

    def evaluate_ValueStringNode(self, value_string_node):
        return value_string_node.value

    def evaluate_JsonListNode(self, jsonlist_node):
        _result = []
        for node in jsonlist_node.nodes:
            _result.append(self.evaluate(node))
        return _result

    
    def interpret(self):
        return self.evaluate(self.parser.parse())
        
def parse():
    l = Lexer(b)
    p = Parser(l)
    i = Interpreter(p)
    return i.interpret()


    
    

        































