"""
Analisador Léxico para a linguagem TONTO
"""
import ply.lex as lex
from .tokens import *

class TontoLexer:
    """Analisador léxico da linguagem TONTO"""

    def __init__(self):
        self.tokens = TOKENS
        self.reserved = RESERVED
        self.lexer = None
        self.errors = []

    def build(self, **kwargs):
        """Constrói o lexer"""
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer

    # Símbolos especiais (ordem importa - do mais longo para o mais curto)
    t_ARROW_LEFT = r'<>--'
    t_ARROW_RIGHT = r'--<>'
    t_ARROW = r'--'
    t_DOTDOT = r'\.\.'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_ASTERISK = r'\*'
    t_AT = r'@'
    t_COLON = r':'
    t_COMMA = r','

    # Ignorar espaços e tabs
    t_ignore = ' \t'

    def t_COMMENT(self, t):
        r'\#.*'
        pass  # Comentários são ignorados, não passados para o parser

    # Números inteiros (para cardinalidades)
    def t_INTEGER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    # Custom DataType: inicia com letra, sem números, sem sublinhado, termina com "DataType"
    def t_CUSTOM_DATATYPE(self, t):
        r'[a-zA-Z][a-zA-Z]*DataType'
        # Validar que não contém números ou sublinhado
        if '_' in t.value or any(c.isdigit() for c in t.value[:-8]):
            t.type = 'INVALID_DATATYPE'
        return t

    # Nome de instância: inicia com letra, pode ter sublinhado, termina com número
    def t_INSTANCE_NAME(self, t):
        r'[a-zA-Z][a-zA-Z_]*[0-9]+'
        return t

    # Nome de classe: inicia com maiúscula, seguido por letras ou sublinhado, sem números
    def t_CLASS_NAME(self, t):
        r'[A-Z][a-zA-Z_]*'
        # Validar que não contém números
        if any(c.isdigit() for c in t.value):
            t.type = 'INVALID_CLASS_NAME'
            return t
        # Verificar se é palavra reservada
        t.type = self.reserved.get(t.value, 'CLASS_NAME')
        return t

    # Nome de relação: inicia com minúscula, seguido por letras ou sublinhado, sem números
    def t_RELATION_NAME(self, t):
        r'[a-z][a-zA-Z_\-]*'
        # Validar que não contém números
        if any(c.isdigit() for c in t.value):
            t.type = 'INVALID_RELATION_NAME'
            return t
        # Verificar se é palavra reservada
        t.type = self.reserved.get(t.value, 'RELATION_NAME')
        return t

    # Rastrear números de linha
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Tratamento de erros léxicos
    def t_error(self, t):
        """Tratamento de erros léxicos"""
        self.errors.append(t)
        t.lexer.skip(1)

    def tokenize(self, data):
        """Tokeniza o código fonte"""
        self.errors.clear()
        self.lexer.input(data)
        tokens = []

        for tok in self.lexer:
            tokens.append(tok)

        return tokens, self.errors

    def get_token_info(self, token):
        """Retorna informações sobre um token para exibição"""
        categoria = ""
        notificacao = ""

        if token.type in CLASS_STEREOTYPES.values():
            categoria = "Estereótipo de Classe"
            notificacao = "OK"
        elif token.type in RELATION_STEREOTYPES.values():
            categoria = "Estereótipo de Relação"
            notificacao = "OK"
        elif token.type in RESERVED_WORDS.values():
            categoria = "Palavra Reservada"
            notificacao = "OK"
        elif token.type in NATIVE_TYPES.values():
            categoria = "Tipo de Dado Nativo"
            notificacao = "OK"
        elif token.type in META_ATTRIBUTES.values():
            categoria = "Meta-atributo"
            notificacao = "OK"
        elif token.type == 'CLASS_NAME':
            categoria = "Nome de Classe"
            notificacao = "OK"
        elif token.type == 'RELATION_NAME':
            categoria = "Nome de Relação"
            notificacao = "OK"
        elif token.type == 'INSTANCE_NAME':
            categoria = "Nome de Instância"
            notificacao = "OK"
        elif token.type == 'CUSTOM_DATATYPE':
            categoria = "Tipo de Dado Customizado"
            notificacao = "OK"
        elif token.type == 'INVALID_CLASS_NAME':
            categoria = "Erro"
            notificacao = "Nome de classe inválido: não deve conter números"
        elif token.type == 'INVALID_RELATION_NAME':
            categoria = "Erro"
            notificacao = "Nome de relação inválido: não deve conter números"
        elif token.type == 'INVALID_DATATYPE':
            categoria = "Erro"
            notificacao = "Tipo customizado inválido: não deve conter números ou sublinhado"
        elif token.type == 'COMMENT':
            categoria = "Comentário"
            notificacao = "OK"
        elif token.type == 'INTEGER':
            categoria = "Literal Numérico"
            notificacao = "OK"
        else:
            categoria = "Símbolo Especial"
            notificacao = "OK"

        return {
            'linha': token.lineno,
            'coluna': token.lexpos,
            'tipo': token.type,
            'valor': token.value,
            'notificacao': notificacao,
            'categoria': categoria
        }
