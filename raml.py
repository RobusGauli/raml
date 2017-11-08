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
LEFT_STRING = 'LEFT_STRING'
RIGHT_STRING = 'RIGHT_STRING'
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
left_string_token = lambda value: Token(LEFT_STRING, value)
right_string_token = lambda value: Token(RIGHT_STRING, value)
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
                return right_string_token(self.variable())
            if self.current_character == '#':
                self.advance()
                return left_string_token(self.variable())
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

class LeftStringNode:

    def __init__(self, token):
        self.token = token
        self.value = self.token.value

    def __repr__(self):
        return 'LeftStringNode({})'.format(self.token.value)

class RightStringNode:

    def __init__(self, token):
        self.token = token
        self.value = self.token.value
    
    
    def __repr__(self):
        return 'RightStringNode({})'.format(self.ast)

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
        assignment_statement: LEFT_STRING ARROW expr
        expr: RIGHT_STRING(COMMA RIGHT_STRING)* | statement_list
        factor: LEFT_STRING | RIGHT_STRING
                
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
        if self.current_token.type == LEFT_STRING:
            return self.assignment_statement()
        return Noop()

    def assignment_statement(self):
        _r = self.factor()
        self.eat(ARROW)
        expr = self.expr()
        return AssignmentNode(_r, expr)
    
    def expr(self):
        if self.current_token.type == RIGHT_STRING:
            _result = self.factor()
            
            expr_node = ExprNode()
            expr_node.nodes.append(_result)
            while self.current_token.type == COMMA:
                self.eat(COMMA)
                expr_node.nodes.append(self.factor())
            
            return expr_node
        if self.current_token.type == LEFT_STRING:
            return self.statement_list()


    def factor(self):
        _token = self.current_token
        if _token.type == LEFT_STRING:
            self.eat(LEFT_STRING)
            return LeftStringNode(_token)
        if _token.type == RIGHT_STRING:
            self.eat(RIGHT_STRING)
            return RightStringNode(_token)
    
             
    
    def error(self):
        raise Exception('Syntaax Error')



class Interpreter:

    def __init__(self, parser):
        self.parser = parser
        self._data = {}
    
    def evaluate(self, ast):
        _method_name = self.evaluate.__name__ + '_' + type(ast).__name__
        return getattr(self, _method_name)(ast)

    def evaluate_LeftStringNode(self, ast):
        return ast.token.value

    def evaluate_RightStringNode(self, ast):
        return ast.token.value


    
    
    def evaluate_ExprNode(self, ast):
        if len(ast.nodes) == 1:
            return self.evaluate(ast.nodes[0])

        _list = []
        for node in ast.nodes:
            _list.append(self.evaluate(node))
        return _list

    def evaluate_StatementListNode(self, ast):
        _result = {}
        for assignment_node in ast.nodes:
            if not isinstance(assignment_node, Noop):
                _result[self.evaluate(assignment_node.left)] = self.evaluate(assignment_node.right)
        return _result

    def evaluate_Noop(self, ast=None):
        pass

    def interpret(self):
        return self.evaluate(self.parser.statement_list())


def loads(text):
    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    return interpreter.interpret()
    


def parse(text):
    lexer = Lexer(text)
    parser = Parser(lexer)
    return parser.statement_list()

;;