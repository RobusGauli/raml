'''
    
    <<
        name -> robus
        age -> 34
        friends -> suman, arjan, shiva, rudra
        fitness ->  <<
                        running -> 100
                        walking -> 300
                    >
        age -> 12
    >>
    
'''
ARROW = 'ARROW'
STRING = 'STRING'
EOF = 'EOF'
COMMA = 'COMMA'
NEW_LINE = 'NEW_LINE'


class Token:

    def __init__(self, _type, value=None):
        self.type = _type
        self.value = value
    
    def __repr__(self):
        return 'Token({}, {})'.format(self.type, self.value)

arrow_token = lambda: Token(ARROW)
string_token = lambda value: Token(STRING, value)
eof_token = lambda: Token(EOF)
comma_token = lambda: Token(COMMA)
new_line_token = lambda: Token(NEW_LINE)

class Lexer:

    def __init__(self, text):
        self.text = text
        self.current_position = 0
    
    @property
    def current_character(self):
        if self.current_position >= len(self.text):
            return None
        return self.text[self.current_position]
    
    @property
    def ahead_character(self):
        _ahead_position = self.current_position + 1
        if _ahead_position >= len(self.text):
            return None
        return self.text[_ahead_position]

    def skip_whitespace(self):
        while self.current_character is not None and self.current_character == ' ' :
            self.advance()
    
    def variable(self):
        #current_character is a variable
        _result = ''
        while self.current_character is not None and self.current_character.isalnum():
            _result += self.current_character
            self.advance()
        return _result
    
    
    def advance(self):
        self.current_position += 1
    
    def new_line(self):
        while self.current_character is not None and self.current_character == '\n':
            self.advance()
        return new_line_token()

    def get_next_token(self):

        while True:
            if self.current_character is None:
                return eof_token()
            if self.current_character == ' ':
                self.skip_whitespace()
                continue
            if self.current_character.isalnum():
                return string_token(self.variable())
            if self.current_character == '-' and self.ahead_character == '>':
                self.advance()
                self.advance()
                return arrow_token()
            if self.current_character == ',':
                self.advance()
                return comma_token()
            if self.current_character == '\n':
                return self.new_line()
            self.error()
    
    def error(self):
        raise Exception('Token Error')

class Noop:
    pass

class AssignmentNode:

    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __repr__(self):
        return 'AssignmentNode({})'.format(self.left)

class StringNode:

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return 'StringNode({})'.format(self.token)

class ExprNode:

    def __init__(self):
        self.nodes = []

class StatementListNode:

    def __init__(self, nodes):
        self.nodes = list(nodes)

class Parser:
    '''Grammar:
        statement_list: statement
                        | statement_list
        statement: assignment_statement
                    | empty
        assignment_statement: factor ARROW expr
        expr: factor(COMMA factor)* | statement_list
        factor: STRING
                
    '''

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
    
    def statement_list(self):
        
        _node = self.statement()
        _nodes = [_node]
        while self.current_token.type == NEW_LINE:
            self.eat(NEW_LINE)
            _nodes.append(self.statement())
        return StatementListNode(_nodes)
    
    def statement(self):
        if self.current_token.type == STRING:
            return self.assignment_statement()
        return Noop()

    def assignment_statement(self):
        _r = self.factor()
        self.eat(ARROW)
        expr = self.expr()
        return AssignmentNode(_r, expr)
    
    def expr(self):
        _result = self.factor()
        
        expr_node = ExprNode()
        expr_node.nodes.append(_result)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            expr_node.nodes.append(self.factor())
        
        return expr_node

    def factor(self):
        _token = self.current_token
        if _token.type == STRING:
            self.eat(STRING)
            return StringNode(_token)
    
             
    
    def error(self):
        raise Exception('Syntaax Error')



class Interpreter:

    def __init__(self, parser):
        self.parser = parser
        self._data = {}
    
    def evaluate(self, ast):
        _method_name = self.evaluate.__name__ + '_' + type(ast).__name__
        return getattr(self, _method_name)(ast)

    def evaluate_StringNode(self, ast):
        return ast.token.value

    def evaluate_AssignmentNode(self, ast):
        self._data[ast.left.token.value] = self.evaluate(ast.right)
    
    def evaluate_ExprNode(self, ast):
        if len(ast.nodes) == 1:
            return self.evaluate(ast.nodes[0])

        _list = []
        for node in ast.nodes:
            _list.append(self.evaluate(node))
        return _list

    def evaluate_StatementListNode(self, ast):
        for node in ast.nodes:
            self.evaluate(node)

    def evaluate_Noop(self, ast=None):
        pass

    def interpret(self):
        return self.evaluate(self.parser.statement_list())


def load(text):
    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.interpret()
    return interpreter._data

