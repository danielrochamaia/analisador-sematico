"""
Definições de tokens e palavras reservadas da linguagem TONTO
"""

# Estereótipos de classe (19 tipos)
CLASS_STEREOTYPES = {
    'event': 'EVENT',
    'situation': 'SITUATION',
    'process': 'PROCESS',
    'category': 'CATEGORY',
    'mixin': 'MIXIN',
    'phaseMixin': 'PHASEMIXIN',
    'roleMixin': 'ROLEMIXIN',
    'historicalRoleMixin': 'HISTORICALROLEMIXIN',
    'kind': 'KIND',
    'collective': 'COLLECTIVE',
    'quantity': 'QUANTITY',
    'quality': 'QUALITY',
    'mode': 'MODE',
    'intrinsicMode': 'INTRINSICMODE',
    'extrinsicMode': 'EXTRINSICMODE',
    'subkind': 'SUBKIND',
    'phase': 'PHASE',
    'role': 'ROLE',
    'historicalRole': 'HISTORICALROLE',
    'relator': 'RELATOR'
}

# Estereótipos de relações (29 tipos)
RELATION_STEREOTYPES = {
    'material': 'MATERIAL',
    'derivation': 'DERIVATION',
    'comparative': 'COMPARATIVE',
    'mediation': 'MEDIATION',
    'characterization': 'CHARACTERIZATION',
    'externalDependence': 'EXTERNALDEPENDENCE',
    'subCollectionOf': 'SUBCOLLECTIONOF',
    'subQualityOf': 'SUBQUALITYOF',
    'componentOf': 'COMPONENTOF',
    'instantiation': 'INSTANTIATION',
    'memberOf': 'MEMBEROF',
    'termination': 'TERMINATION',
    'participational': 'PARTICIPATIONAL',
    'participation': 'PARTICIPATION',
    'historicalDependence': 'HISTORICALDEPENDENCE',
    'creation': 'CREATION',
    'manifestation': 'MANIFESTATION',
    'bringsAbout': 'BRINGSABOUT',
    'triggers': 'TRIGGERS',
    'composition': 'COMPOSITION',
    'aggregation': 'AGGREGATION',
    'inherence': 'INHERENCE',
    'value': 'VALUE',
    'formal': 'FORMAL',
    'constitution': 'CONSTITUTION'
}

# Palavras reservadas
RESERVED_WORDS = {
    'genset': 'GENSET',
    'disjoint': 'DISJOINT',
    'complete': 'COMPLETE',
    'general': 'GENERAL',
    'specifics': 'SPECIFICS',
    'where': 'WHERE',
    'package': 'PACKAGE',
    'import': 'IMPORT',
    'functional-complexes': 'FUNCTIONAL_COMPLEXES',
    'enum': 'ENUM',
    'relation': 'RELATION',
    'overlapping': 'OVERLAPPING',
    'incomplete': 'INCOMPLETE',
    'specializes': 'SPECIALIZES',
    'of': 'OF',
    'relators': 'RELATORS',
    'intrinsic-modes': 'INTRINSIC_MODES'
}

# Tipos de dados nativos
NATIVE_TYPES = {
    'number': 'NUMBER_TYPE',
    'string': 'STRING_TYPE',
    'boolean': 'BOOLEAN_TYPE',
    'date': 'DATE_TYPE',
    'time': 'TIME_TYPE',
    'datetime': 'DATETIME_TYPE'
}

# Meta-atributos
META_ATTRIBUTES = {
    'ordered': 'ORDERED',
    'const': 'CONST',
    'derived': 'DERIVED',
    'subsets': 'SUBSETS',
    'redefines': 'REDEFINES'
}

# Combinar todas as palavras reservadas
RESERVED = {}
RESERVED.update(CLASS_STEREOTYPES)
RESERVED.update(RELATION_STEREOTYPES)
RESERVED.update(RESERVED_WORDS)
RESERVED.update(NATIVE_TYPES)
RESERVED.update(META_ATTRIBUTES)

# Lista de tokens
TOKENS = [
    # Símbolos especiais
    'LBRACE',           # {
    'RBRACE',           # }
    'LPAREN',           # (
    'RPAREN',           # )
    'LBRACKET',         # [
    'RBRACKET',         # ]
    'DOTDOT',           # ..
    'ARROW_LEFT',       # <>--
    'ARROW_RIGHT',      # --<>
    'ARROW',            # --
    'ASTERISK',         # *
    'AT',               # @
    'COLON',            # :
    'COMMA',            # ,

    # Identificadores
    'CLASS_NAME',       # iniciando com maiúscula
    'RELATION_NAME',    # iniciando com minúscula
    'INSTANCE_NAME',    # terminando com número
    'CUSTOM_DATATYPE',  # terminando com DataType

    # Literais
    'INTEGER',          # números inteiros para cardinalidades

    # Comentários e espaços
    'COMMENT',

    # Tokens de erro
    'INVALID_CLASS_NAME',
    'INVALID_RELATION_NAME',
    'INVALID_INSTANCE_NAME',
    'INVALID_DATATYPE',
] + list(RESERVED.values())
