"""
Gramática da Linguagem TONTO em formato BNF (Backus-Naur Form)

Esta gramática define as regras sintáticas para a linguagem TONTO
conforme especificado para a Unidade 2 da disciplina de Compiladores.
"""

TONTO_GRAMMAR = """
# ============================================================================
# GRAMÁTICA TONTO - BNF
# ============================================================================

# Regra inicial
ontology ::= package_list

package_list ::= package
               | package_list package

# 1. DECLARAÇÃO DE PACOTES
package ::= PACKAGE CLASS_NAME LBRACE declarations RBRACE

declarations ::= /* vazio */
               | declarations declaration

declaration ::= class_declaration
              | datatype_declaration
              | enum_declaration
              | generalization_declaration
              | relation_declaration

# 2. DECLARAÇÃO DE CLASSES
class_declaration ::= class_stereotype CLASS_NAME
                    | class_stereotype CLASS_NAME LBRACE class_body RBRACE

class_stereotype ::= KIND | SUBKIND | ROLE | PHASE | CATEGORY | MIXIN
                   | PHASEMIXIN | ROLEMIXIN | HISTORICALROLEMIXIN
                   | COLLECTIVE | QUANTITY | QUALITY | MODE
                   | INTRINSICMODE | EXTRINSICMODE | EVENT | SITUATION
                   | PROCESS | HISTORICALROLE

class_body ::= /* vazio */
             | class_body class_member

class_member ::= attribute_declaration
               | internal_relation_declaration

attribute_declaration ::= RELATION_NAME COLON type_reference

type_reference ::= NATIVE_TYPE
                 | CLASS_NAME
                 | CUSTOM_DATATYPE

# 3. DECLARAÇÃO DE TIPOS DE DADOS
datatype_declaration ::= CUSTOM_DATATYPE LBRACE datatype_body RBRACE

datatype_body ::= /* vazio */
                | datatype_body attribute_declaration

# 4. DECLARAÇÃO DE CLASSES ENUMERADAS
enum_declaration ::= ENUM CLASS_NAME LBRACE instance_list RBRACE

instance_list ::= CLASS_NAME
                | instance_list COMMA CLASS_NAME

# 5. GENERALIZAÇÕES (GENERALIZATION SETS)
generalization_declaration ::= genset_simple
                             | genset_complete

# Forma simples: disjoint complete genset PersonAgeGroup where general Person specifics Child Adult
genset_simple ::= genset_modifiers GENSET CLASS_NAME WHERE
                  GENERAL CLASS_NAME
                  SPECIFICS class_name_list

genset_modifiers ::= /* vazio */
                   | DISJOINT
                   | COMPLETE
                   | OVERLAPPING
                   | INCOMPLETE
                   | DISJOINT COMPLETE
                   | COMPLETE DISJOINT
                   | OVERLAPPING INCOMPLETE
                   | INCOMPLETE OVERLAPPING

# Forma completa com bloco
genset_complete ::= genset_modifiers GENSET CLASS_NAME LBRACE genset_body RBRACE

genset_body ::= GENERAL CLASS_NAME SPECIFICS class_name_list

class_name_list ::= CLASS_NAME
                  | class_name_list CLASS_NAME

# 6. DECLARAÇÃO DE RELAÇÕES

# Relação interna à classe
internal_relation_declaration ::= relation_stereotype cardinality arrow_symbol CLASS_NAME

# Relação externa
relation_declaration ::= AT relation_stereotype RELATION CLASS_NAME arrow_symbol cardinality CLASS_NAME
                       | AT relation_stereotype RELATION CLASS_NAME cardinality arrow_symbol CLASS_NAME

relation_stereotype ::= MATERIAL | MEDIATION | CHARACTERIZATION | DERIVATION
                      | COMPARATIVE | EXTERNALDEPENDENCE | COMPONENTOF
                      | MEMBEROF | SUBCOLLECTIONOF | SUBQUALITYOF
                      | INSTANTIATION | TERMINATION | PARTICIPATIONAL
                      | PARTICIPATION | HISTORICALDEPENDENCE | CREATION
                      | MANIFESTATION | BRINGSABOUT | TRIGGERS | COMPOSITION
                      | AGGREGATION | INHERENCE | VALUE | FORMAL | CONSTITUTION

arrow_symbol ::= ARROW_LEFT
               | ARROW_RIGHT
               | ARROW

cardinality ::= NUMBER DOTDOT NUMBER
              | NUMBER DOTDOT ASTERISK
              | ASTERISK
              | /* vazio */

NUMBER ::= DIGITS

"""

# Mapeamento de construtos para análise
CONSTRUCT_TYPES = {
    'package': 'Declaração de Pacote',
    'class': 'Declaração de Classe',
    'datatype': 'Declaração de Tipo de Dado',
    'enum': 'Declaração de Classe Enumerada',
    'genset': 'Declaração de Generalização',
    'relation': 'Declaração de Relação',
    'attribute': 'Declaração de Atributo',
    'internal_relation': 'Declaração de Relação Interna'
}
