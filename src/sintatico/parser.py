"""
Analisador Sintático para a linguagem TONTO
Implementado com PLY (Python Lex-Yacc)
"""
import ply.yacc as yacc
from ..lexico.tokens import TOKENS


class TontoParser:
    """Analisador sintático da linguagem TONTO"""

    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = TOKENS
        self.parser = None
        self.errors = []

        # Estrutura para armazenar informações da análise
        self.imports = []
        self.packages = []
        self.current_package = None
        self.classes = []
        self.datatypes = []
        self.enums = []
        self.gensets = []
        self.relations = []
        self.attributes = []

    def build(self, **kwargs):
        """Constrói o parser"""
        self.parser = yacc.yacc(module=self, **kwargs)
        return self.parser

    def parse(self, data):
        """Analisa o código fonte"""
        self.errors.clear()
        self.imports.clear()
        self.packages.clear()
        self.classes.clear()
        self.datatypes.clear()
        self.enums.clear()
        self.gensets.clear()
        self.relations.clear()
        self.attributes.clear()

        result = self.parser.parse(data, lexer=self.lexer.lexer)
        return result, self.errors

    def get_analysis_summary(self):
        """Retorna resumo da análise sintática"""
        return {
            'imports': self.imports,
            'packages': self.packages,
            'classes': self.classes,
            'datatypes': self.datatypes,
            'enums': self.enums,
            'gensets': self.gensets,
            'relations': self.relations,
            'attributes': self.attributes,
            'total_errors': len(self.errors)
        }

    def _process_class_body(self, body):
        """
        Processa o corpo de uma classe para vincular estereótipos standalone às relações seguintes.
        Quando encontra um standalone_stereotype seguido de uma relação interna,
        aplica o estereótipo à relação.
        """
        if not body:
            return []

        processed = []
        pending_stereotype = None

        for i, member in enumerate(body):
            # Verifica se é um estereótipo standalone
            if isinstance(member, dict) and member.get('type') == 'pending_stereotype':
                # Guarda o estereótipo para aplicar ao próximo membro
                pending_stereotype = member.get('stereotype')
                continue  # Não adiciona à lista processada

            # Se for uma relação interna e há um estereótipo pendente
            if isinstance(member, dict) and pending_stereotype:
                # Se for uma relação interna, aplica o estereótipo
                if member.get('internal') and member.get('stereotype') is None:
                    member['stereotype'] = pending_stereotype
                    pending_stereotype = None

            # Adiciona o membro processado
            processed.append(member)

        return processed

    # ========================================================================
    # REGRAS DE PRODUÇÃO
    # ========================================================================

    # Regra inicial
    def p_ontology(self, p):
        '''ontology : import_list package_list
                    | package_list'''
        if len(p) == 3:
            p[0] = {'type': 'ontology', 'imports': p[1], 'packages': p[2]}
        else:
            p[0] = {'type': 'ontology', 'imports': [], 'packages': p[1]}

    # Imports
    def p_import_list(self, p):
        '''import_list : import_statement
                       | import_list import_statement'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_import_statement(self, p):
        '''import_statement : IMPORT CLASS_NAME
                            | IMPORT RELATION_NAME'''
        import_info = {
            'module': p[2],
            'line': p.lineno(1)
        }
        self.imports.append(import_info)
        p[0] = import_info

    def p_package_list(self, p):
        '''package_list : package
                        | package_list package'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    # 1. DECLARAÇÃO DE PACOTES
    def p_package_with_braces(self, p):
        '''package : PACKAGE package_name LBRACE declarations RBRACE'''
        package_info = {
            'name': p[2],
            'declarations': p[4],
            'line': p.lineno(1)
        }
        self.packages.append(package_info)
        p[0] = package_info

    def p_package_without_braces(self, p):
        '''package : PACKAGE package_name declarations'''
        package_info = {
            'name': p[2],
            'declarations': p[3],
            'line': p.lineno(1)
        }
        self.packages.append(package_info)
        p[0] = package_info

    def p_package_name(self, p):
        '''package_name : CLASS_NAME
                        | RELATION_NAME'''
        p[0] = p[1]

    def p_declarations_empty(self, p):
        '''declarations : '''
        p[0] = []

    def p_declarations_list(self, p):
        '''declarations : declarations declaration'''
        p[0] = p[1] + [p[2]]

    def p_declaration(self, p):
        '''declaration : class_declaration
                       | datatype_declaration
                       | enum_declaration
                       | generalization_declaration
                       | relation_declaration'''
        p[0] = p[1]

    # 2. DECLARAÇÃO DE CLASSES
    def p_class_declaration_simple(self, p):
        '''class_declaration : class_stereotype CLASS_NAME'''
        class_info = {
            'stereotype': p[1],
            'name': p[2],
            'parents': [],
            'body': [],
            'line': p.lineno(2)
        }
        self.classes.append(class_info)
        p[0] = class_info

    def p_class_declaration_with_specializes(self, p):
        '''class_declaration : class_stereotype CLASS_NAME SPECIALIZES parent_list'''
        class_info = {
            'stereotype': p[1],
            'name': p[2],
            'parents': p[4],
            'body': [],
            'line': p.lineno(2)
        }
        self.classes.append(class_info)
        p[0] = class_info

    def p_class_declaration_with_body(self, p):
        '''class_declaration : class_stereotype CLASS_NAME LBRACE class_body RBRACE'''
        # Processar corpo da classe para vincular estereótipos standalone
        processed_body = self._process_class_body(p[4])

        class_info = {
            'stereotype': p[1],
            'name': p[2],
            'parents': [],
            'body': processed_body,
            'line': p.lineno(2)
        }
        self.classes.append(class_info)
        p[0] = class_info

    def p_class_declaration_with_specializes_and_body(self, p):
        '''class_declaration : class_stereotype CLASS_NAME SPECIALIZES parent_list LBRACE class_body RBRACE'''
        # Processar corpo da classe para vincular estereótipos standalone
        processed_body = self._process_class_body(p[6])

        class_info = {
            'stereotype': p[1],
            'name': p[2],
            'parents': p[4],
            'body': processed_body,
            'line': p.lineno(2)
        }
        self.classes.append(class_info)
        p[0] = class_info

    # Declarações com "of <partition>"
    def p_class_declaration_with_partition(self, p):
        '''class_declaration : class_stereotype CLASS_NAME OF partition_name'''
        class_info = {
            'stereotype': p[1],
            'name': p[2],
            'partition': p[4],
            'parents': [],
            'body': [],
            'line': p.lineno(2)
        }
        self.classes.append(class_info)
        p[0] = class_info

    def p_class_declaration_with_partition_and_specializes(self, p):
        '''class_declaration : class_stereotype CLASS_NAME OF partition_name SPECIALIZES parent_list'''
        class_info = {
            'stereotype': p[1],
            'name': p[2],
            'partition': p[4],
            'parents': p[6],
            'body': [],
            'line': p.lineno(2)
        }
        self.classes.append(class_info)
        p[0] = class_info

    def p_class_declaration_with_partition_and_body(self, p):
        '''class_declaration : class_stereotype CLASS_NAME OF partition_name LBRACE class_body RBRACE'''
        processed_body = self._process_class_body(p[6])

        class_info = {
            'stereotype': p[1],
            'name': p[2],
            'partition': p[4],
            'parents': [],
            'body': processed_body,
            'line': p.lineno(2)
        }
        self.classes.append(class_info)
        p[0] = class_info

    def p_class_declaration_with_partition_specializes_and_body(self, p):
        '''class_declaration : class_stereotype CLASS_NAME OF partition_name SPECIALIZES parent_list LBRACE class_body RBRACE'''
        processed_body = self._process_class_body(p[8])

        class_info = {
            'stereotype': p[1],
            'name': p[2],
            'partition': p[4],
            'parents': p[6],
            'body': processed_body,
            'line': p.lineno(2)
        }
        self.classes.append(class_info)
        p[0] = class_info

    def p_partition_name(self, p):
        '''partition_name : FUNCTIONAL_COMPLEXES
                          | RELATORS
                          | INTRINSIC_MODES'''
        p[0] = p[1]

    # Lista de classes pai (para herança)
    def p_parent_list_single(self, p):
        '''parent_list : CLASS_NAME'''
        p[0] = [p[1]]

    def p_parent_list_multiple(self, p):
        '''parent_list : parent_list COMMA CLASS_NAME'''
        p[0] = p[1] + [p[3]]

    def p_class_stereotype(self, p):
        '''class_stereotype : KIND
                            | SUBKIND
                            | ROLE
                            | PHASE
                            | CATEGORY
                            | MIXIN
                            | PHASEMIXIN
                            | ROLEMIXIN
                            | HISTORICALROLEMIXIN
                            | COLLECTIVE
                            | QUANTITY
                            | QUALITY
                            | MODE
                            | INTRINSICMODE
                            | EXTRINSICMODE
                            | EVENT
                            | SITUATION
                            | PROCESS
                            | HISTORICALROLE
                            | RELATOR'''
        p[0] = p[1]

    def p_class_body_empty(self, p):
        '''class_body : '''
        p[0] = []

    def p_class_body_list(self, p):
        '''class_body : class_body class_member'''
        p[0] = p[1] + [p[2]]

    def p_class_member(self, p):
        '''class_member : attribute_declaration
                        | internal_relation_declaration
                        | standalone_stereotype'''
        p[0] = p[1]

    def p_standalone_stereotype(self, p):
        '''standalone_stereotype : AT relation_stereotype'''
        # Estereótipo sozinho em uma linha (será usado na próxima relação)
        p[0] = {
            'type': 'pending_stereotype',
            'stereotype': p[2],
            'line': p.lineno(1)
        }

    def p_attribute_declaration(self, p):
        '''attribute_declaration : RELATION_NAME COLON type_reference
                                  | RELATION_NAME COLON type_reference cardinality'''
        attr_info = {
            'name': p[1],
            'type': p[3],
            'cardinality': p[4] if len(p) == 5 else None,
            'line': p.lineno(1)
        }
        self.attributes.append(attr_info)
        p[0] = attr_info

    def p_type_reference(self, p):
        '''type_reference : NUMBER_TYPE
                          | STRING_TYPE
                          | BOOLEAN_TYPE
                          | DATE_TYPE
                          | TIME_TYPE
                          | DATETIME_TYPE
                          | CLASS_NAME
                          | CUSTOM_DATATYPE'''
        p[0] = p[1]

    # 3. DECLARAÇÃO DE TIPOS DE DADOS
    def p_datatype_declaration(self, p):
        '''datatype_declaration : CUSTOM_DATATYPE LBRACE datatype_body RBRACE'''
        datatype_info = {
            'name': p[1],
            'attributes': p[3],
            'line': p.lineno(1)
        }
        self.datatypes.append(datatype_info)
        p[0] = datatype_info

    def p_datatype_body_empty(self, p):
        '''datatype_body : '''
        p[0] = []

    def p_datatype_body_list(self, p):
        '''datatype_body : datatype_body attribute_declaration'''
        p[0] = p[1] + [p[2]]

    # 4. DECLARAÇÃO DE CLASSES ENUMERADAS
    def p_enum_declaration(self, p):
        '''enum_declaration : ENUM CLASS_NAME LBRACE instance_list RBRACE'''
        enum_info = {
            'name': p[2],
            'instances': p[4],
            'line': p.lineno(1)
        }
        self.enums.append(enum_info)
        p[0] = enum_info

    def p_instance_list_single(self, p):
        '''instance_list : instance_name'''
        p[0] = [p[1]]

    def p_instance_list_multiple(self, p):
        '''instance_list : instance_list COMMA instance_name'''
        p[0] = p[1] + [p[3]]

    def p_instance_name(self, p):
        '''instance_name : CLASS_NAME
                         | INSTANCE_NAME'''
        p[0] = p[1]

    # 5. GENERALIZAÇÕES (GENERALIZATION SETS)

    # Forma simples
    def p_generalization_simple(self, p):
        '''generalization_declaration : genset_modifiers GENSET genset_name WHERE GENERAL CLASS_NAME SPECIFICS class_name_list'''
        genset_info = {
            'name': p[3],
            'modifiers': p[1],
            'general': p[6],
            'specifics': p[8],
            'line': p.lineno(2)
        }
        self.gensets.append(genset_info)
        p[0] = genset_info

    # Forma completa
    def p_generalization_complete(self, p):
        '''generalization_declaration : genset_modifiers GENSET genset_name LBRACE genset_body RBRACE'''
        genset_info = {
            'name': p[3],
            'modifiers': p[1],
            'general': p[5]['general'],
            'specifics': p[5]['specifics'],
            'line': p.lineno(2)
        }
        self.gensets.append(genset_info)
        p[0] = genset_info

    def p_genset_name(self, p):
        '''genset_name : CLASS_NAME
                       | RELATION_NAME'''
        p[0] = p[1]

    def p_genset_modifiers_empty(self, p):
        '''genset_modifiers : '''
        p[0] = []

    def p_genset_modifiers_disjoint(self, p):
        '''genset_modifiers : DISJOINT'''
        p[0] = ['disjoint']

    def p_genset_modifiers_complete(self, p):
        '''genset_modifiers : COMPLETE'''
        p[0] = ['complete']

    def p_genset_modifiers_overlapping(self, p):
        '''genset_modifiers : OVERLAPPING'''
        p[0] = ['overlapping']

    def p_genset_modifiers_incomplete(self, p):
        '''genset_modifiers : INCOMPLETE'''
        p[0] = ['incomplete']

    def p_genset_modifiers_disjoint_complete(self, p):
        '''genset_modifiers : DISJOINT COMPLETE
                            | COMPLETE DISJOINT'''
        p[0] = ['disjoint', 'complete']

    def p_genset_modifiers_overlapping_incomplete(self, p):
        '''genset_modifiers : OVERLAPPING INCOMPLETE
                            | INCOMPLETE OVERLAPPING'''
        p[0] = ['overlapping', 'incomplete']

    def p_genset_body(self, p):
        '''genset_body : GENERAL CLASS_NAME SPECIFICS class_name_list'''
        p[0] = {
            'general': p[2],
            'specifics': p[4]
        }

    def p_class_name_list_single(self, p):
        '''class_name_list : CLASS_NAME'''
        p[0] = [p[1]]

    def p_class_name_list_multiple(self, p):
        '''class_name_list : class_name_list COMMA CLASS_NAME'''
        p[0] = p[1] + [p[3]]

    # CARDINALIDADES
    def p_cardinality_asterisk(self, p):
        '''cardinality : LBRACKET ASTERISK RBRACKET'''
        p[0] = {'min': 0, 'max': '*', 'text': '[*]'}

    def p_cardinality_single(self, p):
        '''cardinality : LBRACKET INTEGER RBRACKET'''
        p[0] = {'min': p[2], 'max': p[2], 'text': f'[{p[2]}]'}

    def p_cardinality_range(self, p):
        '''cardinality : LBRACKET INTEGER DOTDOT INTEGER RBRACKET'''
        p[0] = {'min': p[2], 'max': p[4], 'text': f'[{p[2]}..{p[4]}]'}

    def p_cardinality_range_asterisk(self, p):
        '''cardinality : LBRACKET INTEGER DOTDOT ASTERISK RBRACKET'''
        p[0] = {'min': p[2], 'max': '*', 'text': f'[{p[2]}..*]'}

    def p_cardinality_optional(self, p):
        '''cardinality : '''
        p[0] = None

    # 6. DECLARAÇÃO DE RELAÇÕES

    # Relação interna (dentro de classe)
    def p_internal_relation_declaration(self, p):
        '''internal_relation_declaration : relation_stereotype cardinality arrow_symbol cardinality CLASS_NAME
                                         | relation_stereotype RELATION_NAME cardinality arrow_symbol cardinality CLASS_NAME
                                         | relation_stereotype arrow_symbol CLASS_NAME
                                         | relation_stereotype RELATION_NAME arrow_symbol CLASS_NAME
                                         | arrow_symbol RELATION_NAME arrow_symbol cardinality CLASS_NAME
                                         | arrow_symbol RELATION_NAME arrow_symbol CLASS_NAME
                                         | cardinality arrow_symbol cardinality CLASS_NAME
                                         | cardinality arrow_symbol CLASS_NAME'''
        # Verificar se começa com estereótipo, seta ou cardinalidade
        starts_with_arrow = (p[1] == '--' or p[1] == '<>--' or p[1] == '--<>')
        starts_with_cardinality = isinstance(p[1], dict) and 'min' in p[1]

        if starts_with_cardinality:
            # Sintaxe: [card] -- [card] Classe  OU  [card] -- Classe
            if len(p) == 5:
                # [1..*] -- [1] Unidade_Basica_De_Saude
                relation_info = {
                    'stereotype': None,
                    'name': None,
                    'source_cardinality': p[1],
                    'arrow': p[2],
                    'target_cardinality': p[3],
                    'target': p[4],
                    'internal': True,
                    'line': p.lineno(2)
                }
            else:  # len(p) == 4
                # [1..*] -- Unidade_Basica_De_Saude
                relation_info = {
                    'stereotype': None,
                    'name': None,
                    'source_cardinality': p[1],
                    'arrow': p[2],
                    'target_cardinality': None,
                    'target': p[3],
                    'internal': True,
                    'line': p.lineno(2)
                }
        elif starts_with_arrow:
            # Sintaxe: -- nome -- [card] Classe  OU  -- nome -- Classe
            if len(p) == 6:
                # -- involvesRental -- [1] RentalCar
                relation_info = {
                    'stereotype': None,
                    'name': p[2],
                    'source_cardinality': None,
                    'arrow': p[3],
                    'target_cardinality': p[4],
                    'target': p[5],
                    'internal': True,
                    'line': p.lineno(1)
                }
            else:  # len(p) == 5
                # -- involvesMediator -- ResponsibleEmployee
                relation_info = {
                    'stereotype': None,
                    'name': p[2],
                    'source_cardinality': None,
                    'arrow': p[3],
                    'target_cardinality': None,
                    'target': p[4],
                    'internal': True,
                    'line': p.lineno(1)
                }
        else:
            # Começa com estereótipo
            if len(p) == 6:
                # @mediation [1..*] -- [1] Paciente
                relation_info = {
                    'stereotype': p[1],
                    'name': None,
                    'source_cardinality': p[2],
                    'arrow': p[3],
                    'target_cardinality': p[4],
                    'target': p[5],
                    'internal': True,
                    'line': p.lineno(1)
                }
            elif len(p) == 7:
                # @mediation rel [1..*] -- [1] Paciente
                relation_info = {
                    'stereotype': p[1],
                    'name': p[2],
                    'source_cardinality': p[3],
                    'arrow': p[4],
                    'target_cardinality': p[5],
                    'target': p[6],
                    'internal': True,
                    'line': p.lineno(1)
                }
            elif len(p) == 4:
                # @mediation -- Paciente
                relation_info = {
                    'stereotype': p[1],
                    'name': None,
                    'source_cardinality': None,
                    'arrow': p[2],
                    'target_cardinality': None,
                    'target': p[3],
                    'internal': True,
                    'line': p.lineno(1)
                }
            else:  # len(p) == 5
                # @mediation rel -- Paciente
                relation_info = {
                    'stereotype': p[1],
                    'name': p[2],
                    'source_cardinality': None,
                    'arrow': p[3],
                    'target_cardinality': None,
                    'target': p[4],
                    'internal': True,
                    'line': p.lineno(1)
                }
        self.relations.append(relation_info)
        p[0] = relation_info

    # Relação externa
    def p_relation_declaration(self, p):
        '''relation_declaration : AT relation_stereotype RELATION CLASS_NAME cardinality arrow_symbol RELATION_NAME arrow_symbol cardinality CLASS_NAME
                                | AT relation_stereotype RELATION CLASS_NAME cardinality arrow_symbol cardinality CLASS_NAME
                                | AT relation_stereotype RELATION CLASS_NAME arrow_symbol CLASS_NAME
                                | relation_stereotype CLASS_NAME cardinality arrow_symbol cardinality CLASS_NAME
                                | relation_stereotype CLASS_NAME arrow_symbol CLASS_NAME'''
        if len(p) == 11:
            # @material relation Paciente [1..*] -- consultado_Por -- [1..*] Medico
            relation_info = {
                'stereotype': p[2],
                'source': p[4],
                'source_cardinality': p[5],
                'arrow': p[6],
                'relation_name': p[7],
                'arrow2': p[8],
                'target_cardinality': p[9],
                'target': p[10],
                'internal': False,
                'line': p.lineno(1)
            }
        elif len(p) == 9:
            # @material relation Paciente [1..*] -- [1..*] Medico
            relation_info = {
                'stereotype': p[2],
                'source': p[4],
                'source_cardinality': p[5],
                'arrow': p[6],
                'target_cardinality': p[7],
                'target': p[8],
                'internal': False,
                'line': p.lineno(1)
            }
        elif len(p) == 7:
            # @mediation relation Employee -- EmploymentContract
            relation_info = {
                'stereotype': p[2],
                'source': p[4],
                'source_cardinality': None,
                'arrow': p[5],
                'target_cardinality': None,
                'target': p[6],
                'internal': False,
                'line': p.lineno(1)
            }
        elif len(p) == 6:
            # material University [1..*] <>-- [1] Department
            relation_info = {
                'stereotype': p[1],
                'source': p[2],
                'source_cardinality': p[3],
                'arrow': p[4],
                'target_cardinality': p[5],
                'target': p[6],
                'internal': False,
                'line': p.lineno(1)
            }
        else:
            # material University <>-- Department
            relation_info = {
                'stereotype': p[1],
                'source': p[2],
                'source_cardinality': None,
                'arrow': p[3],
                'target_cardinality': None,
                'target': p[4],
                'internal': False,
                'line': p.lineno(1)
            }
        self.relations.append(relation_info)
        p[0] = relation_info

    def p_relation_stereotype(self, p):
        '''relation_stereotype : MATERIAL
                               | MEDIATION
                               | CHARACTERIZATION
                               | DERIVATION
                               | COMPARATIVE
                               | EXTERNALDEPENDENCE
                               | COMPONENTOF
                               | MEMBEROF
                               | SUBCOLLECTIONOF
                               | SUBQUALITYOF
                               | INSTANTIATION
                               | TERMINATION
                               | PARTICIPATIONAL
                               | PARTICIPATION
                               | HISTORICALDEPENDENCE
                               | CREATION
                               | MANIFESTATION
                               | BRINGSABOUT
                               | TRIGGERS
                               | COMPOSITION
                               | AGGREGATION
                               | INHERENCE
                               | VALUE
                               | FORMAL
                               | CONSTITUTION'''
        p[0] = p[1]

    def p_arrow_symbol(self, p):
        '''arrow_symbol : ARROW_LEFT
                        | ARROW_RIGHT
                        | ARROW'''
        p[0] = p[1]

    # ========================================================================
    # TRATAMENTO DE ERROS
    # ========================================================================

    def p_error(self, p):
        """Tratamento de erros sintáticos"""
        if p:
            error = {
                'linha': p.lineno,
                'coluna': p.lexpos,
                'tipo': 'Erro Sintático',
                'token': p.type,
                'valor': p.value,
                'mensagem': f"Sintaxe inválida: token inesperado '{p.value}' (tipo: {p.type})",
                'sugestao': self._get_error_suggestion(p)
            }
            self.errors.append(error)

            # Tentar recuperar do erro
            self.parser.errok()
        else:
            error = {
                'linha': -1,
                'coluna': -1,
                'tipo': 'Erro Sintático',
                'token': 'EOF',
                'valor': '',
                'mensagem': "Fim de arquivo inesperado",
                'sugestao': "Verifique se todas as chaves e parênteses foram fechados corretamente"
            }
            self.errors.append(error)

    def _get_error_suggestion(self, p):
        """Gera sugestões de correção baseadas no tipo de erro"""
        token_type = p.type
        token_value = p.value

        # Mensagens específicas e detalhadas por tipo de token
        suggestions = {
            # Nomes
            'CLASS_NAME': f"Nome de classe '{token_value}' inesperado. Verifique se:\n"
                         f"  • Está usando o estereótipo correto (kind, role, phase, etc.)\n"
                         f"  • A sintaxe está completa: 'kind {token_value}' ou 'kind {token_value} specializes ClassePai'",

            'RELATION_NAME': f"Nome de relação '{token_value}' inesperado. Nomes de relação devem:\n"
                            f"  • Começar com letra minúscula\n"
                            f"  • Não conter números\n"
                            f"  • Ser usados em contexto de relação ou atributo",

            'INSTANCE_NAME': f"Nome '{token_value}' foi reconhecido como INSTÂNCIA (termina com número).\n"
                           f"  ⚠️  Se for nome de CLASSE: remova os números. Nomes de classe não podem ter números.\n"
                           f"  ⚠️  Se for nome de INSTÂNCIA de enum: use em contexto apropriado.\n"
                           f"  💡 Sugestão: renomeie para formato sem números (ex: '{str(token_value).rstrip('0123456789')}_One')",

            # Blocos
            'LBRACE': "Esperado '{' para abrir um bloco. Verifique se:\n"
                     "  • Declaração de package, class, enum ou genset está completa\n"
                     "  • Não faltam palavras-chave antes da chave",

            'RBRACE': "Chave de fechamento '}' inesperada. Possíveis problemas:\n"
                     "  • Bloco vazio ou incompleto\n"
                     "  • Declaração anterior mal formada\n"
                     "  • Chave de fechamento extra",

            # Cardinalidades
            'LBRACKET': "Cardinalidade mal formatada. Use:\n"
                       "  • [*] para qualquer número\n"
                       "  • [n] para exatamente n\n"
                       "  • [n..m] para range\n"
                       "  • [n..*] para n ou mais",

            'RBRACKET': "Fechamento de cardinalidade ']' inesperado. Verifique:\n"
                       "  • Se a cardinalidade foi aberta com '['\n"
                       "  • Se o formato está correto: [n], [n..m], [n..*], ou [*]",

            'INTEGER': f"Número '{token_value}' fora de contexto. Números só são válidos em:\n"
                      f"  • Cardinalidades: [1], [1..*], [2..5]\n"
                      f"  • Final de nomes de instâncias: Planeta1, Item2",

            'ASTERISK': "Asterisco '*' fora de contexto. Use apenas em:\n"
                       "  • Cardinalidades: [*] ou [1..*]",

            'DOTDOT': "Operador '..' fora de contexto. Use apenas em:\n"
                     "  • Ranges de cardinalidade: [1..5], [0..*]",

            # Palavras reservadas
            'PACKAGE': "Palavra 'package' inesperada. Sintaxe correta:\n"
                      "  • package NomePacote { declarações }\n"
                      "  • package NomePacote (sem chaves, tudo depois pertence ao pacote)",

            'IMPORT': "Palavra 'import' inesperada. Imports devem estar:\n"
                     "  • No início do arquivo\n"
                     "  • Antes de qualquer package\n"
                     "  • Sintaxe: import NomeModulo",

            'SPECIALIZES': "Palavra 'specializes' fora de contexto. Use em declarações de classe:\n"
                          "  • kind NomeClasse specializes ClassePai\n"
                          "  • role NomeClasse specializes Pai1, Pai2  (herança múltipla)",

            'GENSET': "Palavra 'genset' inesperada. Sintaxe correta:\n"
                     "  • [modificadores] genset Nome { general ClasseMae specifics Filha1, Filha2 }\n"
                     "  • Modificadores opcionais: disjoint, complete, overlapping, incomplete",

            'WHERE': "Palavra 'where' inesperada. Use em gensets (forma simplificada):\n"
                    "  • genset Nome where general Mae specifics Filha1 Filha2",

            'GENERAL': "Palavra 'general' fora de contexto. Use em gensets:\n"
                      "  • general NomeClasseMae",

            'SPECIFICS': "Palavra 'specifics' fora de contexto. Use em gensets:\n"
                        "  • specifics Classe1, Classe2, Classe3",

            'ENUM': "Palavra 'enum' inesperada. Sintaxe correta:\n"
                   "  • enum NomeEnum { Valor1, Valor2, Valor3 }",

            'RELATION': "Palavra 'relation' fora de contexto. Use em relações externas:\n"
                       "  • @estereotipo relation Classe1 -- Classe2",

            # Setas
            'ARROW': "Seta '--' fora de contexto. Use em:\n"
                    "  • Relações externas: @material relation Classe1 -- Classe2\n"
                    "  • Relações internas: @mediation -- [1] ClasseAlvo",

            'ARROW_LEFT': "Seta '<>--' fora de contexto. Use em relações de composição/agregação",

            'ARROW_RIGHT': "Seta '--<>' fora de contexto. Use em relações de composição/agregação",

            # Símbolos
            'COMMA': "Vírgula ',' inesperada. Vírgulas são usadas para separar:\n"
                    "  • Valores de enum: enum Cores { Azul, Verde, Vermelho }\n"
                    "  • Classes em gensets: specifics Filho1, Filho2\n"
                    "  • Classes em herança múltipla: specializes Pai1, Pai2",

            'COLON': "Dois-pontos ':' fora de contexto. Use em declarações de atributo:\n"
                    "  • nomeAtributo : TipoDado",

            'AT': "Símbolo '@' fora de contexto. Use antes de estereótipos de relação:\n"
                 "  • @mediation\n"
                 "  • @material relation Classe1 -- Classe2",

            # Estereótipos
            'MEDIATION': "Estereótipo 'mediation' fora de contexto. Use:\n"
                        "  • Em relações internas de relator: @mediation -- ClasseAlvo\n"
                        "  • Em relações externas: @mediation relation Classe1 -- Classe2",

            'MATERIAL': "Estereótipo 'material' fora de contexto. Use em relações materiais:\n"
                       "  • @material relation Agente -- Acao",
        }

        # Retornar sugestão específica ou genérica
        return suggestions.get(token_type,
                             f"Token '{token_value}' (tipo: {token_type}) não esperado neste contexto.\n"
                             f"  💡 Verifique a estrutura da declaração e consulte a documentação TONTO.")
