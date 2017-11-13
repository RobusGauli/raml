class AST:
    def __init__(self, token=None):
        self.token = token

class JsonObjectNode(AST):

    def __init__(self, nodes=[]):
        self.nodes = list(nodes)
        super().__init__()
    

    def __repr__(self):
        return 'JSONObject({})'.format(self.nodes)


class JsonListNode(AST):

    def __init__(self):
        self.nodes = []
        super().__init__()
    
    def __repr__(self):
        return 'JSONLIST()'

class AssignmentNode(AST):

    def __init__(self, left, right, token):
        self.left = left
        self.right = right
        self.token = token
        super().__init__(token)

    def __repr__(self):
        return 'AssignmentNode({})'.format(self.token)


class EmptyNode(AST):
    pass


class StringNode(AST):
    name = ''
    def __init__(self, token):
        self.value = token.value
        super().__init__(token)
    
    def __repr__(self):
        return '{}({})'.format(self.name, self.value)


class KeyStringNode(StringNode):
    name = 'KeyStringNode'

class ValueStringNode(StringNode):
    name = 'ValueStringNode'


    '''
        json_object: (statement)*
                        
        statement: assignment_statement
                    | empty
        assignment_statement: KEYSTRING COLON expr
        expr: factor | LSBRACKET ((COMMA factor)* RSBRACKET 
        factor: VALUESTRING
                | json_object
                '''

    '''

(   #name: robus,
    #age: 45,
    #friends: [rita, sita, gita, tita],
    #fitness: (
        #running: 44,
        #walking: 56
    )
)
'''

a = '''

(   
    #fitness: (
        #love: sadf
    )
)
'''