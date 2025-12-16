"""
Validador de Padrões de Projeto de Ontologias (ODPs)

Este módulo valida 6 padrões principais:
1. Subkind Pattern
2. Role Pattern
3. Phase Pattern
4. Relator Pattern
5. Mode Pattern
6. RoleMixin Pattern
"""


class PatternValidator:
    """
    Classe principal para validação de padrões de ontologias.

    Recebe os dados da análise sintática e valida se os padrões
    estão completos ou incompletos.
    """

    def __init__(self, analysis_data):
        """
        Inicializa o validador com os dados da análise sintática.

        Args:
            analysis_data: Dicionário com classes, gensets, relações, etc.
        """
        self.classes = analysis_data.get('classes', [])
        self.gensets = analysis_data.get('gensets', [])
        self.relations = analysis_data.get('relations', [])

        # Armazena padrões encontrados
        self.complete_patterns = []    # Padrões completos (corretos)
        self.incomplete_patterns = []  # Padrões incompletos (com erros)

    def validate_all(self):
        """
        Executa validação de todos os padrões.

        Returns:
            Dicionário com chaves 'complete' e 'incomplete' contendo
            listas de padrões validados formatados para a GUI
        """
        # Limpar resultados anteriores
        self.complete_patterns = []
        self.incomplete_patterns = []

        # Validar cada padrão
        self._validate_subkind_pattern()
        self._validate_role_pattern()
        self._validate_phase_pattern()
        self._validate_relator_pattern()
        self._validate_mode_pattern()
        self._validate_rolemixin_pattern()

        # Formatar resultados para a GUI
        formatted_complete = [self._format_complete_pattern(p) for p in self.complete_patterns]
        formatted_incomplete = [self._format_incomplete_pattern(p) for p in self.incomplete_patterns]

        # Retornar dicionário com os resultados formatados
        return {
            'complete': formatted_complete,
            'incomplete': formatted_incomplete
        }

    def _format_complete_pattern(self, pattern_data):
        """
        Formata um padrão completo para exibição na GUI.

        Args:
            pattern_data: Dicionário com dados do padrão validado

        Returns:
            Dicionário formatado com 'pattern', 'details' e 'line'
        """
        pattern_type = pattern_data['type']
        line = pattern_data.get('line', '-')

        # Criar descrição detalhada baseada no tipo de padrão
        if 'Subkind' in pattern_type:
            details = f"Kind '{pattern_data['kind']}' com subkinds {pattern_data['subkinds']} e genset '{pattern_data['genset']}'"
        elif 'Role' in pattern_type and 'RoleMixin' not in pattern_type:
            details = f"Kind '{pattern_data['kind']}' com roles {pattern_data['roles']} e genset '{pattern_data['genset']}'"
        elif 'Phase' in pattern_type:
            details = f"Kind '{pattern_data['kind']}' com phases {pattern_data['phases']} e genset '{pattern_data['genset']}'"
        elif 'Relator' in pattern_type:
            details = f"Relator '{pattern_data['relator']}' com {pattern_data['mediations']} mediações"
        elif 'Mode' in pattern_type:
            details = f"Mode '{pattern_data['mode']}' com @characterization e @externalDependence"
        elif 'RoleMixin' in pattern_type:
            details = f"RoleMixin '{pattern_data['rolemixin']}' com roles {pattern_data['roles']} e genset '{pattern_data['genset']}'"
        else:
            details = str(pattern_data)

        return {
            'pattern': pattern_type,
            'details': details,
            'line': line
        }

    def _format_incomplete_pattern(self, pattern_data):
        """
        Formata um padrão incompleto para exibição na GUI.

        Args:
            pattern_data: Dicionário com dados do padrão validado

        Returns:
            Dicionário formatado com 'pattern', 'error', 'suggestion' e 'line'
        """
        return {
            'pattern': pattern_data['type'],
            'error': pattern_data['error'],
            'suggestion': pattern_data['suggestion'],
            'line': pattern_data.get('line', '-')
        }

    # =========================================================================
    # 1. SUBKIND PATTERN
    # =========================================================================

    def _validate_subkind_pattern(self):
        """
        Valida o padrão Subkind.

        REGRA: Se há subkinds especializando um kind, deve haver um
               genset DISJOINT COMPLETE agrupando esses subkinds.

        Exemplo correto:
            kind ClassName
            subkind SubclassName1 specializes ClassName
            subkind SubclassName2 specializes ClassName

            disjoint complete genset Kind_Subkind_Genset_Name {
                general ClassName
                specifics SubclassName1, SubclassName2
            }
        """
        # Passo 1: Encontrar todos os kinds
        kinds = [c for c in self.classes if c['stereotype'] == 'kind']

        for kind in kinds:
            kind_name = kind['name']

            # Passo 2: Encontrar subkinds que especializam este kind
            subkinds = [
                c for c in self.classes
                if c['stereotype'] == 'subkind' and kind_name in c.get('parents', [])
            ]

            # Se não há subkinds, não há padrão a validar
            if len(subkinds) < 2:
                continue

            # Passo 3: Verificar se existe genset para esses subkinds
            genset_found = self._find_genset_for_classes(
                kind_name,
                [s['name'] for s in subkinds],
                required_modifiers=['disjoint', 'complete']
            )

            # Passo 4: Registrar resultado
            if genset_found:
                self.complete_patterns.append({
                    'type': 'Subkind Pattern',
                    'kind': kind_name,
                    'subkinds': [s['name'] for s in subkinds],
                    'genset': genset_found['name'],
                    'line': kind['line']
                })
            else:
                self.incomplete_patterns.append({
                    'type': 'Subkind Pattern',
                    'kind': kind_name,
                    'subkinds': [s['name'] for s in subkinds],
                    'error': 'Falta genset disjoint complete',
                    'suggestion': f'Adicione: disjoint complete genset {kind_name}_Genset {{ general {kind_name} specifics {", ".join([s["name"] for s in subkinds])} }}',
                    'line': kind['line']
                })

    # =========================================================================
    # 2. ROLE PATTERN
    # =========================================================================

    def _validate_role_pattern(self):
        """
        Valida o padrão Role.

        REGRA: Se há roles especializando um kind, deve haver um
               genset COMPLETE (disjoint NÃO se aplica a roles).

        Exemplo correto:
            kind ClassName
            role Role_Name1 specializes ClassName
            role Role_Name2 specializes ClassName

            complete genset Class_Role_Genset_Name {
                general ClassName
                specifics Role_Name1, Role_Name2
            }
        """
        # Passo 1: Encontrar todos os kinds
        kinds = [c for c in self.classes if c['stereotype'] == 'kind']

        for kind in kinds:
            kind_name = kind['name']

            # Passo 2: Encontrar roles que especializam este kind
            roles = [
                c for c in self.classes
                if c['stereotype'] == 'role' and kind_name in c.get('parents', [])
            ]

            # Se não há roles suficientes, não há padrão
            if len(roles) < 2:
                continue

            # Passo 3: Verificar genset (deve ser complete, NÃO disjoint)
            genset_found = self._find_genset_for_classes(
                kind_name,
                [r['name'] for r in roles],
                required_modifiers=['complete'],
                forbidden_modifiers=['disjoint']  # Roles NÃO podem ser disjoint
            )

            # Passo 4: Registrar resultado
            if genset_found:
                self.complete_patterns.append({
                    'type': 'Role Pattern',
                    'kind': kind_name,
                    'roles': [r['name'] for r in roles],
                    'genset': genset_found['name'],
                    'line': kind['line']
                })
            else:
                self.incomplete_patterns.append({
                    'type': 'Role Pattern',
                    'kind': kind_name,
                    'roles': [r['name'] for r in roles],
                    'error': 'Falta genset complete (sem disjoint)',
                    'suggestion': f'Adicione: complete genset {kind_name}_Role_Genset {{ general {kind_name} specifics {", ".join([r["name"] for r in roles])} }}',
                    'line': kind['line']
                })

    # =========================================================================
    # 3. PHASE PATTERN
    # =========================================================================

    def _validate_phase_pattern(self):
        """
        Valida o padrão Phase.

        REGRA: Se há phases especializando um kind, deve haver um
               genset DISJOINT (obrigatório), COMPLETE (opcional).

        Exemplo correto:
            kind ClassName
            phase Phase_Name1 specializes ClassName
            phase Phase_Name2 specializes ClassName
            phase Phase_NameN specializes ClassName

            disjoint complete genset Class_Phase_Genset_Name {
                general ClassName
                specifics Phase_Name1, Phase_Name2, Phase_NameN
            }
        """
        # Passo 1: Encontrar todos os kinds
        kinds = [c for c in self.classes if c['stereotype'] == 'kind']

        for kind in kinds:
            kind_name = kind['name']

            # Passo 2: Encontrar phases que especializam este kind
            phases = [
                c for c in self.classes
                if c['stereotype'] == 'phase' and kind_name in c.get('parents', [])
            ]

            # Se não há phases suficientes, não há padrão
            if len(phases) < 2:
                continue

            # Passo 3: Verificar genset (DEVE ter disjoint)
            genset_found = self._find_genset_for_classes(
                kind_name,
                [p['name'] for p in phases],
                required_modifiers=['disjoint']  # Disjoint é obrigatório
            )

            # Passo 4: Registrar resultado
            if genset_found:
                self.complete_patterns.append({
                    'type': 'Phase Pattern',
                    'kind': kind_name,
                    'phases': [p['name'] for p in phases],
                    'genset': genset_found['name'],
                    'line': kind['line']
                })
            else:
                self.incomplete_patterns.append({
                    'type': 'Phase Pattern',
                    'kind': kind_name,
                    'phases': [p['name'] for p in phases],
                    'error': 'Falta genset disjoint (obrigatório para phases)',
                    'suggestion': f'Adicione: disjoint complete genset {kind_name}_Phase_Genset {{ general {kind_name} specifics {", ".join([p["name"] for p in phases])} }}',
                    'line': kind['line']
                })

    # =========================================================================
    # 4. RELATOR PATTERN
    # =========================================================================

    def _validate_relator_pattern(self):
        """
        Valida o padrão Relator.

        REGRA: Um relator deve ter pelo menos duas relações @mediation
               conectando a roles (ou kinds).

        Exemplo correto:
            kind ClassName1
            kind ClassName2
            role Role_Name1 specializes ClassName1
            role Role_Name2 specializes ClassName2

            relator Relator_Name {
                @mediation [1..*] -- [1..*] Role_Name1
                @mediation [1..*] -- [1..*] Role_Name2
            }
        """
        # Passo 1: Encontrar todos os relators
        relators = [c for c in self.classes if c['stereotype'] == 'relator']

        for relator in relators:
            relator_name = relator['name']

            # Passo 2: Encontrar relações @mediation dentro do relator
            mediations = [
                r for r in self.relations
                if r.get('internal') and r.get('stereotype') == 'mediation'
                # Verificar se pertence a este relator comparando linhas próximas
            ]

            # Filtrar mediations que estão no corpo deste relator
            # (simplificado: assume que relações internas pertencem ao relator mais próximo)
            relator_mediations = []
            for med in mediations:
                # Verificar se a mediação está dentro do corpo do relator
                if relator.get('body'):
                    for member in relator['body']:
                        if member.get('stereotype') == 'mediation':
                            relator_mediations.append(member)

            # Passo 3: Validar (deve ter pelo menos 2 mediações)
            if len(relator_mediations) >= 2:
                self.complete_patterns.append({
                    'type': 'Relator Pattern',
                    'relator': relator_name,
                    'mediations': len(relator_mediations),
                    'line': relator['line']
                })
            else:
                self.incomplete_patterns.append({
                    'type': 'Relator Pattern',
                    'relator': relator_name,
                    'mediations': len(relator_mediations),
                    'error': f'Relator deve ter pelo menos 2 mediações (tem {len(relator_mediations)})',
                    'suggestion': f'Adicione relações @mediation dentro do relator {relator_name}',
                    'line': relator['line']
                })

    # =========================================================================
    # 5. MODE PATTERN
    # =========================================================================

    def _validate_mode_pattern(self):
        """
        Valida o padrão Mode.

        REGRA: Um mode deve ter relações @characterization e @externalDependence.

        Exemplo correto:
            kind ClassName1
            kind ClassName2
            mode Mode_Name1 {
                @characterization [1..*] -- [1] ClassName1
                @externalDependence [1..*] -- [1] ClassName2
            }
        """
        # Passo 1: Encontrar todos os modes
        modes = [c for c in self.classes if c['stereotype'] == 'mode']

        for mode in modes:
            mode_name = mode['name']

            # Passo 2: Verificar se tem characterization e externalDependence
            has_characterization = False
            has_external_dependence = False

            if mode.get('body'):
                for member in mode['body']:
                    if member.get('stereotype') == 'characterization':
                        has_characterization = True
                    if member.get('stereotype') == 'externalDependence':
                        has_external_dependence = True

            # Passo 3: Validar
            if has_characterization and has_external_dependence:
                self.complete_patterns.append({
                    'type': 'Mode Pattern',
                    'mode': mode_name,
                    'line': mode['line']
                })
            else:
                missing = []
                if not has_characterization:
                    missing.append('@characterization')
                if not has_external_dependence:
                    missing.append('@externalDependence')

                self.incomplete_patterns.append({
                    'type': 'Mode Pattern',
                    'mode': mode_name,
                    'error': f'Faltam relações: {", ".join(missing)}',
                    'suggestion': f'Adicione {" e ".join(missing)} dentro do mode {mode_name}',
                    'line': mode['line']
                })

    # =========================================================================
    # 6. ROLEMIXIN PATTERN
    # =========================================================================

    def _validate_rolemixin_pattern(self):
        """
        Valida o padrão RoleMixin.

        REGRA: Um roleMixin deve ter:
               - Roles que o especializam
               - Um genset agrupando esses roles

        Exemplo correto:
            kind ClassName1
            kind ClassName2
            roleMixin RoleMixin_Name
            role Role_Name1 specializes ClassName1, RoleMixin_Name
            role Role_Name2 specializes ClassName2, RoleMixin_Name

            disjoint complete genset RoleMixin_Genset_Name {
                general RoleMixin_Name
                specifics Role_Name1, Role_Name2
            }
        """
        # Passo 1: Encontrar todos os rolemixins
        rolemixins = [c for c in self.classes if c['stereotype'] == 'roleMixin']

        for rolemixin in rolemixins:
            rolemixin_name = rolemixin['name']

            # Passo 2: Encontrar roles que especializam este rolemixin
            roles = [
                c for c in self.classes
                if c['stereotype'] == 'role' and rolemixin_name in c.get('parents', [])
            ]

            # Se não há roles, padrão incompleto
            if len(roles) < 2:
                self.incomplete_patterns.append({
                    'type': 'RoleMixin Pattern',
                    'rolemixin': rolemixin_name,
                    'error': f'Precisa de pelo menos 2 roles especializando {rolemixin_name}',
                    'suggestion': f'Adicione roles que especializam {rolemixin_name}',
                    'line': rolemixin['line']
                })
                continue

            # Passo 3: Verificar se existe genset
            genset_found = self._find_genset_for_classes(
                rolemixin_name,
                [r['name'] for r in roles],
                required_modifiers=['disjoint', 'complete']
            )

            # Passo 4: Registrar resultado
            if genset_found:
                self.complete_patterns.append({
                    'type': 'RoleMixin Pattern',
                    'rolemixin': rolemixin_name,
                    'roles': [r['name'] for r in roles],
                    'genset': genset_found['name'],
                    'line': rolemixin['line']
                })
            else:
                self.incomplete_patterns.append({
                    'type': 'RoleMixin Pattern',
                    'rolemixin': rolemixin_name,
                    'roles': [r['name'] for r in roles],
                    'error': 'Falta genset disjoint complete',
                    'suggestion': f'Adicione: disjoint complete genset {rolemixin_name}_Genset {{ general {rolemixin_name} specifics {", ".join([r["name"] for r in roles])} }}',
                    'line': rolemixin['line']
                })

    # =========================================================================
    # MÉTODOS AUXILIARES
    # =========================================================================

    def _find_genset_for_classes(self, general_class, specific_classes,
                                  required_modifiers=None, forbidden_modifiers=None):
        """
        Procura um genset que agrupa as classes especificadas.

        Args:
            general_class: Nome da classe geral
            specific_classes: Lista de nomes das classes específicas
            required_modifiers: Modificadores que DEVEM estar presentes
            forbidden_modifiers: Modificadores que NÃO podem estar presentes

        Returns:
            Genset encontrado ou None
        """
        required_modifiers = required_modifiers or []
        forbidden_modifiers = forbidden_modifiers or []

        for genset in self.gensets:
            # Verificar se a classe geral corresponde
            if genset.get('general') != general_class:
                continue

            # Verificar se as classes específicas estão todas no genset
            genset_specifics = genset.get('specifics', [])
            if not all(spec in genset_specifics for spec in specific_classes):
                continue

            # Verificar modificadores obrigatórios
            genset_modifiers = genset.get('modifiers', [])
            if not all(mod in genset_modifiers for mod in required_modifiers):
                continue

            # Verificar modificadores proibidos
            if any(mod in genset_modifiers for mod in forbidden_modifiers):
                continue

            # Genset encontrado!
            return genset

        return None

    def get_summary(self):
        """
        Retorna resumo da validação.

        Returns:
            Dicionário com estatísticas
        """
        return {
            'total_complete': len(self.complete_patterns),
            'total_incomplete': len(self.incomplete_patterns),
            'complete_by_type': self._count_by_type(self.complete_patterns),
            'incomplete_by_type': self._count_by_type(self.incomplete_patterns)
        }

    def _count_by_type(self, patterns):
        """Conta padrões por tipo."""
        counts = {}
        for pattern in patterns:
            ptype = pattern['type']
            counts[ptype] = counts.get(ptype, 0) + 1
        return counts
