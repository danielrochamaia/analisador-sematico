"""
Interface gráfica principal do analisador TONTO
Integra análise léxica, sintática e semântica
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from ..lexico.lexico import TontoLexer
from ..sintatico.parser import TontoParser
from ..semantico.pattern_validator import PatternValidator


class ToolTip:
    """
    Classe para criar tooltips (balõezinhos) que aparecem ao passar o mouse
    """
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.text = ""

    def show_tip(self, text, x, y):
        """Mostra o tooltip"""
        if self.tip_window or not text:
            return

        self.text = text
        # Posicionar o tooltip próximo ao mouse
        x = x + 20
        y = y + 10

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # Criar frame com borda
        frame = tk.Frame(tw, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        frame.pack()

        # Adicionar texto com quebra de linha
        label = tk.Label(frame, text=text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.FLAT,
                        font=("Arial", 9), wraplength=400, padx=8, pady=6)
        label.pack()

    def hide_tip(self):
        """Esconde o tooltip"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class TontoAnalyzerGUI:
    """Interface gráfica do analisador TONTO - Léxico, Sintático e Semântico"""

    def __init__(self, root):
        self.root = root

        # Inicializar analisadores
        self.lexer = TontoLexer()
        self.lexer.build()

        self.parser = TontoParser(self.lexer)
        self.parser.build(debug=False, write_tables=False)

        self._setup_window()
        self._create_notebook()
        self._create_menu()

    def _setup_window(self):
        """Configurações da janela principal"""
        self.root.title("Analisador TONTO - Léxico, Sintático e Semântico")
        self.root.configure(background="white")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        self.root.minsize(width=1000, height=700)

    def _create_notebook(self):
        """Cria abas para diferentes visualizações"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Área de código fonte (topo)
        code_frame = tk.LabelFrame(main_frame, text="Código Fonte TONTO",
                                   font=('Arial', 11, 'bold'), bg="white", fg="#333")
        code_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

        # Editor de código com números de linha
        self.code_text = scrolledtext.ScrolledText(code_frame, font=('Courier New', 10),
                                                   height=12, wrap=tk.WORD)
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botões de ação
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(button_frame, text="Limpar", bg="#FFE0E0", fg="black",
                 font=('Arial', 10, 'bold'), command=self.clear_all,
                 relief=tk.RAISED, bd=2, padx=20, pady=5).pack(side=tk.RIGHT, padx=5)

        tk.Button(button_frame, text="Analisar", bg="#D4EDDA", fg="black",
                 font=('Arial', 10, 'bold'), command=self.analyze_code,
                 relief=tk.RAISED, bd=2, padx=20, pady=5).pack(side=tk.RIGHT, padx=5)

        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Aba 1: Análise Léxica
        self.tab_lexical = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_lexical, text="📝 Análise Léxica")
        self._create_lexical_tab()

        # Aba 2: Análise Sintática
        self.tab_syntactic = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_syntactic, text="🔍 Análise Sintática")
        self._create_syntactic_tab()

        # Aba 3: Análise Semântica
        self.tab_semantic = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_semantic, text="🎯 Análise Semântica")
        self._create_semantic_tab()

        # Aba 4: Relatório de Erros
        self.tab_errors = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_errors, text="❌ Relatório de Erros")
        self._create_errors_tab()

    def _create_lexical_tab(self):
        """Cria aba de análise léxica"""
        # Visão analítica
        frame_tokens = tk.LabelFrame(self.tab_lexical, text="Tokens Identificados",
                                     font=('Arial', 10, 'bold'), bg="white")
        frame_tokens.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ('linha', 'coluna', 'token', 'lexema', 'categoria')
        self.lexical_tree = ttk.Treeview(frame_tokens, columns=columns,
                                        show='headings', height=10)

        self.lexical_tree.heading("linha", text='Linha')
        self.lexical_tree.heading("coluna", text='Coluna')
        self.lexical_tree.heading("token", text='Token')
        self.lexical_tree.heading("lexema", text='Lexema')
        self.lexical_tree.heading("categoria", text='Categoria')

        self.lexical_tree.column("linha", width=60)
        self.lexical_tree.column("coluna", width=60)
        self.lexical_tree.column("token", width=150)
        self.lexical_tree.column("lexema", width=150)
        self.lexical_tree.column("categoria", width=200)

        self.lexical_tree.tag_configure('erro', background='#ffcccc')
        self.lexical_tree.tag_configure('ok', background='#e6ffe6')

        scroll_lex = ttk.Scrollbar(frame_tokens, orient=tk.VERTICAL,
                                  command=self.lexical_tree.yview)
        self.lexical_tree.configure(yscrollcommand=scroll_lex.set)

        self.lexical_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0), pady=5)
        scroll_lex.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0,5))

        # Resumo léxico
        frame_summary_lex = tk.LabelFrame(self.tab_lexical, text="Resumo da Análise Léxica",
                                         font=('Arial', 10, 'bold'), bg="white")
        frame_summary_lex.pack(fill=tk.X, padx=10, pady=5)

        self.lexical_summary_text = tk.Text(frame_summary_lex, height=4,
                                           font=('Courier New', 9), bg="#f0f0f0")
        self.lexical_summary_text.pack(fill=tk.X, padx=5, pady=5)

    def _create_syntactic_tab(self):
        """Cria aba de análise sintática"""
        # Tabela de síntese
        frame_syn = tk.LabelFrame(self.tab_syntactic,
                                 text="Tabela de Síntese dos Construtos",
                                 font=('Arial', 10, 'bold'), bg="white")
        frame_syn.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ('construto', 'quantidade', 'detalhes')
        self.syntactic_tree = ttk.Treeview(frame_syn, columns=columns,
                                          show='tree headings', height=15)

        self.syntactic_tree.heading("#0", text='Tipo')
        self.syntactic_tree.heading("construto", text='Construto')
        self.syntactic_tree.heading("quantidade", text='Quantidade')
        self.syntactic_tree.heading("detalhes", text='Detalhes')

        self.syntactic_tree.column("#0", width=200)
        self.syntactic_tree.column("construto", width=200)
        self.syntactic_tree.column("quantidade", width=100)
        self.syntactic_tree.column("detalhes", width=400)

        scroll_syn = ttk.Scrollbar(frame_syn, orient=tk.VERTICAL,
                                  command=self.syntactic_tree.yview)
        self.syntactic_tree.configure(yscrollcommand=scroll_syn.set)

        self.syntactic_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0), pady=5)
        scroll_syn.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0,5))

    def _create_semantic_tab(self):
        """Cria aba de análise semântica - Validação de ODPs"""
        # Frame principal dividido em duas partes
        main_frame = tk.Frame(self.tab_semantic, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ===== PARTE 1: Padrões Completos (CORRETOS) =====
        frame_complete = tk.LabelFrame(main_frame,
                                       text="✅ Padrões Completos (Corretos)",
                                       font=('Arial', 10, 'bold'),
                                       bg="white",
                                       fg="#2e7d32")  # Verde
        frame_complete.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Treeview para padrões completos
        columns_complete = ('tipo', 'detalhes', 'linha')
        self.semantic_complete_tree = ttk.Treeview(frame_complete,
                                                   columns=columns_complete,
                                                   show='headings',
                                                   height=8)

        self.semantic_complete_tree.heading("tipo", text='Tipo de Padrão')
        self.semantic_complete_tree.heading("detalhes", text='Detalhes')
        self.semantic_complete_tree.heading("linha", text='Linha')

        self.semantic_complete_tree.column("tipo", width=200)
        self.semantic_complete_tree.column("detalhes", width=500)
        self.semantic_complete_tree.column("linha", width=80)

        self.semantic_complete_tree.tag_configure('complete', background='#e8f5e9')

        scroll_complete = ttk.Scrollbar(frame_complete, orient=tk.VERTICAL,
                                       command=self.semantic_complete_tree.yview)
        self.semantic_complete_tree.configure(yscrollcommand=scroll_complete.set)

        self.semantic_complete_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                                        padx=(5,0), pady=5)
        scroll_complete.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0,5))

        # ===== PARTE 2: Padrões Incompletos (COM ERROS) =====
        frame_incomplete = tk.LabelFrame(main_frame,
                                        text="⚠️ Padrões Incompletos (Com Erros)",
                                        font=('Arial', 10, 'bold'),
                                        bg="white",
                                        fg="#d32f2f")  # Vermelho
        frame_incomplete.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Treeview para padrões incompletos
        columns_incomplete = ('tipo', 'erro', 'sugestao', 'linha')
        self.semantic_incomplete_tree = ttk.Treeview(frame_incomplete,
                                                     columns=columns_incomplete,
                                                     show='headings',
                                                     height=8)

        self.semantic_incomplete_tree.heading("tipo", text='Tipo de Padrão')
        self.semantic_incomplete_tree.heading("erro", text='Erro Encontrado')
        self.semantic_incomplete_tree.heading("sugestao", text='Sugestão de Correção')
        self.semantic_incomplete_tree.heading("linha", text='Linha')

        self.semantic_incomplete_tree.column("tipo", width=200)
        self.semantic_incomplete_tree.column("erro", width=250)
        self.semantic_incomplete_tree.column("sugestao", width=350)
        self.semantic_incomplete_tree.column("linha", width=80)

        self.semantic_incomplete_tree.tag_configure('incomplete', background='#ffebee')

        scroll_incomplete = ttk.Scrollbar(frame_incomplete, orient=tk.VERTICAL,
                                         command=self.semantic_incomplete_tree.yview)
        self.semantic_incomplete_tree.configure(yscrollcommand=scroll_incomplete.set)

        self.semantic_incomplete_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                                          padx=(5,0), pady=5)
        scroll_incomplete.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0,5))

    def _create_errors_tab(self):
        """Cria aba de relatório de erros"""
        frame_err = tk.LabelFrame(self.tab_errors,
                                 text="Erros e Sugestões de Correção",
                                 font=('Arial', 10, 'bold'), bg="white")
        frame_err.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Adicionar instruções para o usuário
        instruction_frame = tk.Frame(frame_err, bg="white")
        instruction_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        tk.Label(instruction_frame,
                text="💡 Dica: Passe o mouse sobre uma célula para ver o texto completo | Duplo-clique para abrir detalhes",
                bg="white", fg="#666", font=('Arial', 9, 'italic')).pack(anchor=tk.W)

        columns = ('linha', 'tipo', 'mensagem', 'sugestao')
        self.errors_tree = ttk.Treeview(frame_err, columns=columns,
                                       show='headings', height=20)

        self.errors_tree.heading("linha", text='Linha')
        self.errors_tree.heading("tipo", text='Tipo de Erro')
        self.errors_tree.heading("mensagem", text='Mensagem')
        self.errors_tree.heading("sugestao", text='Sugestão de Correção')

        self.errors_tree.column("linha", width=60)
        self.errors_tree.column("tipo", width=120)
        self.errors_tree.column("mensagem", width=350)
        self.errors_tree.column("sugestao", width=400)

        self.errors_tree.tag_configure('lexico', background='#ffe6e6')
        self.errors_tree.tag_configure('sintatico', background='#fff3e6')

        scroll_err = ttk.Scrollbar(frame_err, orient=tk.VERTICAL,
                                  command=self.errors_tree.yview)
        self.errors_tree.configure(yscrollcommand=scroll_err.set)

        self.errors_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,0), pady=5)
        scroll_err.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0,5))

        # ====================================================================
        # ADICIONAR FUNCIONALIDADES DE VISUALIZAÇÃO
        # ====================================================================

        # Tooltip para quando passar o mouse
        self.error_tooltip = ToolTip(self.errors_tree)

        # Evento: Mostrar tooltip ao passar o mouse
        self.errors_tree.bind('<Motion>', self._show_error_tooltip)
        # Evento: Esconder tooltip ao sair
        self.errors_tree.bind('<Leave>', lambda e: self.error_tooltip.hide_tip())
        # Evento: Abrir janela de detalhes ao dar duplo-clique
        self.errors_tree.bind('<Double-Button-1>', self._show_error_details)

    def _show_error_tooltip(self, event):
        """Mostra tooltip com o texto completo ao passar o mouse"""
        # Identificar a região clicada
        region = self.errors_tree.identify_region(event.x, event.y)

        if region == "cell":
            # Identificar a coluna
            column = self.errors_tree.identify_column(event.x)
            # Identificar o item (linha)
            item = self.errors_tree.identify_row(event.y)

            if item:
                # Pegar valores da linha
                values = self.errors_tree.item(item, 'values')

                # Mapear coluna para índice
                col_map = {'#1': 0, '#2': 1, '#3': 2, '#4': 3}
                col_idx = col_map.get(column)

                if col_idx is not None and col_idx < len(values):
                    text = str(values[col_idx])

                    # Mostrar tooltip apenas se o texto for longo
                    if len(text) > 40:
                        self.error_tooltip.hide_tip()
                        x, y = event.x_root, event.y_root
                        self.error_tooltip.show_tip(text, x, y)
                    else:
                        self.error_tooltip.hide_tip()
                else:
                    self.error_tooltip.hide_tip()
            else:
                self.error_tooltip.hide_tip()
        else:
            self.error_tooltip.hide_tip()

    def _show_error_details(self, event):
        """Abre janela com detalhes completos do erro ao dar duplo-clique"""
        # Identificar o item clicado
        item = self.errors_tree.identify_row(event.y)

        if not item:
            return

        # Pegar valores da linha
        values = self.errors_tree.item(item, 'values')

        if not values or len(values) < 4:
            return

        linha, tipo, mensagem, sugestao = values

        # Criar janela de detalhes
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Detalhes do Erro - Linha {linha}")
        details_window.geometry("700x400")
        details_window.configure(bg="white")

        # Tornar modal
        details_window.transient(self.root)
        details_window.grab_set()

        # Frame principal
        main_frame = tk.Frame(details_window, bg="white", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Linha (informação do tipo de erro integrada)
        info_frame = tk.Frame(main_frame, bg="white")
        info_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(info_frame, text=f"⚠️ {tipo} | ", bg="white",
                font=('Arial', 11, 'bold'), fg="#d32f2f").pack(side=tk.LEFT)
        tk.Label(info_frame, text=f"📍 Linha: ", bg="white",
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        tk.Label(info_frame, text=linha, bg="white",
                font=('Arial', 10)).pack(side=tk.LEFT)

        # Mensagem
        msg_frame = tk.LabelFrame(main_frame, text="Mensagem do Erro",
                                 font=('Arial', 10, 'bold'), bg="white", fg="#333")
        msg_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        msg_text = tk.Text(msg_frame, wrap=tk.WORD, font=('Arial', 10),
                          bg="#fff9e6", height=4, padx=10, pady=10)
        msg_text.insert(1.0, mensagem)
        msg_text.config(state=tk.DISABLED)
        msg_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sugestão
        sug_frame = tk.LabelFrame(main_frame, text="💡 Sugestão de Correção",
                                 font=('Arial', 10, 'bold'), bg="white", fg="#333")
        sug_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        sug_text = tk.Text(sug_frame, wrap=tk.WORD, font=('Arial', 10),
                          bg="#e8f5e9", height=4, padx=10, pady=10)
        sug_text.insert(1.0, sugestao)
        sug_text.config(state=tk.DISABLED)
        sug_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botão fechar
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Fechar", command=details_window.destroy,
                 bg="#E3F2FD", fg="black", font=('Arial', 10, 'bold'),
                 padx=30, pady=8, relief=tk.RAISED, bd=2 ).pack(side=tk.RIGHT)

        # Centralizar janela
        details_window.update_idletasks()
        x = (details_window.winfo_screenwidth() // 2) - (details_window.winfo_width() // 2)
        y = (details_window.winfo_screenheight() // 2) - (details_window.winfo_height() // 2)
        details_window.geometry(f"+{x}+{y}")

    def _create_menu(self):
        """Cria o menu da aplicação"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir Arquivo...", command=self.open_file,
                             accelerator="Ctrl+O")
        file_menu.add_command(label="Salvar Como...", command=self.save_file,
                             accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit,
                             accelerator="Ctrl+Q")

        # Menu Análise
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Análise", menu=analysis_menu)
        analysis_menu.add_command(label="Analisar Código", command=self.analyze_code,
                                 accelerator="F5")
        analysis_menu.add_command(label="Limpar Tudo", command=self.clear_all,
                                 accelerator="Ctrl+L")

        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Documentação TONTO", command=self.show_help)
        help_menu.add_command(label="Sobre", command=self.show_about)

        # Atalhos de teclado
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-l>', lambda e: self.clear_all())
        self.root.bind('<F5>', lambda e: self.analyze_code())

    def analyze_code(self):
        """Executa análise léxica e sintática"""
        code = self.code_text.get(1.0, tk.END)

        if not code.strip():
            messagebox.showwarning("Aviso", "Por favor, insira algum código para analisar")
            return

        # Limpar visualizações anteriores
        self._clear_results()

        # ANÁLISE LÉXICA
        tokens, lex_errors = self.lexer.tokenize(code)

        # Mostrar tokens
        for token in tokens:
            info = self.lexer.get_token_info(token)
            tag = 'erro' if info['categoria'] == 'Erro' else 'ok'
            values = (info['linha'], info['coluna'], info['tipo'],
                     info['valor'], info['categoria'])
            self.lexical_tree.insert('', tk.END, values=values, tags=(tag,))

        # Resumo léxico
        self._show_lexical_summary(tokens, lex_errors)

        # ANÁLISE SINTÁTICA
        try:
            result, syn_errors = self.parser.parse(code)
            summary = self.parser.get_analysis_summary()

            # Mostrar síntese sintática
            self._show_syntactic_summary(summary)

            # ANÁLISE SEMÂNTICA (Validação de ODPs)
            # Só executar se não houver erros sintáticos que impedem a análise
            if not syn_errors:
                validator = PatternValidator(summary)
                semantic_results = validator.validate_all()
                self._show_semantic_results(semantic_results)

            # Mostrar erros
            self._show_errors(lex_errors, syn_errors)

            # Mensagem de sucesso se não houver erros
            if not lex_errors and not syn_errors:
                messagebox.showinfo("Análise Concluída",
                                   "✅ Código analisado com sucesso!\nNenhum erro encontrado.")
                self.notebook.select(self.tab_syntactic)
            else:
                messagebox.showwarning("Análise Concluída com Erros",
                                      f"⚠️ Foram encontrados {len(lex_errors) + len(syn_errors)} erro(s).\n"
                                      f"Verifique a aba 'Relatório de Erros'.")
                self.notebook.select(self.tab_errors)

        except Exception as e:
            messagebox.showerror("Erro na Análise",
                                f"Ocorreu um erro durante a análise:\n{str(e)}")

    def _show_lexical_summary(self, tokens, errors):
        """Mostra resumo da análise léxica"""
        total_tokens = len(tokens)
        total_errors = len(errors)

        # Contar categorias
        categories = {}
        for token in tokens:
            info = self.lexer.get_token_info(token)
            cat = info['categoria']
            categories[cat] = categories.get(cat, 0) + 1

        summary = f"Total de Tokens: {total_tokens}\n"
        summary += f"Erros Léxicos: {total_errors}\n"
        summary += f"Categorias: {', '.join(f'{k}({v})' for k, v in sorted(categories.items()))}\n"

        self.lexical_summary_text.delete(1.0, tk.END)
        self.lexical_summary_text.insert(1.0, summary)

    def _show_syntactic_summary(self, summary):
        """Mostra síntese da análise sintática"""
        # Pacotes
        if summary['packages']:
            pkg_node = self.syntactic_tree.insert('', tk.END, text='📦 Pacotes',
                                                  values=('', len(summary['packages']), ''))
            for pkg in summary['packages']:
                self.syntactic_tree.insert(pkg_node, tk.END, text=f"  {pkg['name']}",
                                         values=(pkg['name'], '', f"Linha {pkg['line']}"))

        # Classes
        if summary['classes']:
            class_node = self.syntactic_tree.insert('', tk.END, text='📋 Classes',
                                                   values=('', len(summary['classes']), ''))
            for cls in summary['classes']:
                details = f"{cls['stereotype']} - Linha {cls['line']}"
                self.syntactic_tree.insert(class_node, tk.END, text=f"  {cls['name']}",
                                         values=(cls['name'], '', details))

        # Tipos de Dados
        if summary['datatypes']:
            dt_node = self.syntactic_tree.insert('', tk.END, text='🔤 Tipos de Dados',
                                                values=('', len(summary['datatypes']), ''))
            for dt in summary['datatypes']:
                details = f"Linha {dt['line']}, {len(dt['attributes'])} atributo(s)"
                self.syntactic_tree.insert(dt_node, tk.END, text=f"  {dt['name']}",
                                         values=(dt['name'], '', details))

        # Enumerações
        if summary['enums']:
            enum_node = self.syntactic_tree.insert('', tk.END, text='📝 Classes Enumeradas',
                                                  values=('', len(summary['enums']), ''))
            for enum in summary['enums']:
                details = f"Linha {enum['line']}, Instâncias: {', '.join(enum['instances'])}"
                self.syntactic_tree.insert(enum_node, tk.END, text=f"  {enum['name']}",
                                         values=(enum['name'], len(enum['instances']), details))

        # Generalizações
        if summary['gensets']:
            gen_node = self.syntactic_tree.insert('', tk.END, text='🌳 Generalizações',
                                                 values=('', len(summary['gensets']), ''))
            for gen in summary['gensets']:
                modifiers = ', '.join(gen['modifiers']) if gen['modifiers'] else 'nenhum'
                details = f"Linha {gen['line']}, Modificadores: {modifiers}"
                details += f", Geral: {gen['general']}, Específicas: {', '.join(gen['specifics'])}"
                self.syntactic_tree.insert(gen_node, tk.END, text=f"  {gen['name']}",
                                         values=(gen['name'], len(gen['specifics']), details))

        # Relações
        if summary['relations']:
            rel_node = self.syntactic_tree.insert('', tk.END, text='🔗 Relações',
                                                 values=('', len(summary['relations']), ''))
            for rel in summary['relations']:
                tipo = "Interna" if rel['internal'] else "Externa"
                estereotipo = rel.get('stereotype', 'sem estereótipo')

                # Criar nome descritivo para a relação
                if rel.get('name'):
                    # Se tem nome explícito, usar ele
                    nome = rel['name']
                else:
                    # Se não tem nome, criar descrição baseada em estereótipo e alvo
                    target = rel.get('target', 'desconhecido')
                    if estereotipo and estereotipo != 'sem estereótipo':
                        nome = f"{estereotipo} → {target}"
                    else:
                        nome = f"→ {target}"

                details = f"Linha {rel['line']}, Tipo: {tipo}, Estereótipo: {estereotipo}"
                self.syntactic_tree.insert(rel_node, tk.END, text=f"  {nome}",
                                         values=(nome, '', details))

    def _show_semantic_results(self, results):
        """
        Mostra resultados da análise semântica - Validação de ODPs

        Parâmetros:
            results: dicionário com 'complete' e 'incomplete' patterns
        """
        # Limpar árvores anteriores
        self.semantic_complete_tree.delete(*self.semantic_complete_tree.get_children())
        self.semantic_incomplete_tree.delete(*self.semantic_incomplete_tree.get_children())

        # ===== PADRÕES COMPLETOS (Corretos) =====
        for pattern in results['complete']:
            # Formato: tipo, detalhes, linha
            tipo = pattern['pattern']
            detalhes = pattern['details']
            linha = pattern.get('line', '-')

            self.semantic_complete_tree.insert('', tk.END,
                                              values=(tipo, detalhes, linha),
                                              tags=('complete',))

        # ===== PADRÕES INCOMPLETOS (Com Erros) =====
        for pattern in results['incomplete']:
            # Formato: tipo, erro, sugestão, linha
            tipo = pattern['pattern']
            erro = pattern['error']
            sugestao = pattern['suggestion']
            linha = pattern.get('line', '-')

            self.semantic_incomplete_tree.insert('', tk.END,
                                                 values=(tipo, erro, sugestao, linha),
                                                 tags=('incomplete',))

    def _show_errors(self, lex_errors, syn_errors):
        """Mostra relatório de erros"""
        # Erros léxicos
        for error in lex_errors:
            msg = f"Caractere inválido: '{error.value[0]}'"
            sugestao = "Remova ou substitua este caractere por um símbolo válido"
            self.errors_tree.insert('', tk.END,
                                   values=(error.lineno, 'Erro Léxico', msg, sugestao),
                                   tags=('lexico',))

        # Erros sintáticos
        for error in syn_errors:
            self.errors_tree.insert('', tk.END,
                                   values=(error['linha'], error['tipo'],
                                          error['mensagem'], error['sugestao']),
                                   tags=('sintatico',))

    def _clear_results(self):
        """Limpa resultados das análises"""
        self.lexical_tree.delete(*self.lexical_tree.get_children())
        self.syntactic_tree.delete(*self.syntactic_tree.get_children())
        self.semantic_complete_tree.delete(*self.semantic_complete_tree.get_children())
        self.semantic_incomplete_tree.delete(*self.semantic_incomplete_tree.get_children())
        self.errors_tree.delete(*self.errors_tree.get_children())
        self.lexical_summary_text.delete(1.0, tk.END)

    def clear_all(self):
        """Limpa tudo"""
        self.code_text.delete(1.0, tk.END)
        self._clear_results()

    def open_file(self):
        """Abre arquivo TONTO"""
        filepath = filedialog.askopenfilename(
            title="Abrir arquivo TONTO",
            filetypes=(("Arquivos TONTO", "*.tonto"),
                      ("Arquivos de texto", "*.txt"),
                      ("Todos os arquivos", "*.*"))
        )

        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.code_text.delete(1.0, tk.END)
                    self.code_text.insert(1.0, content)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir arquivo:\n{str(e)}")

    def save_file(self):
        """Salva arquivo TONTO"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".tonto",
            filetypes=(("Arquivos TONTO", "*.tonto"),
                      ("Arquivos de texto", "*.txt"),
                      ("Todos os arquivos", "*.*"))
        )

        if filepath:
            try:
                content = self.code_text.get(1.0, tk.END)
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content.rstrip())
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")

    def show_help(self):
        """Mostra documentação"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Documentação - Linguagem TONTO")
        help_window.geometry("900x700")

        text = scrolledtext.ScrolledText(help_window, font=('Arial', 10),
                                        wrap=tk.WORD, padx=15, pady=15)
        text.pack(fill=tk.BOTH, expand=True)

        help_content = """
LINGUAGEM TONTO - DOCUMENTAÇÃO COMPLETA
========================================

[Conteúdo da documentação aqui...]
        """

        text.insert(1.0, help_content)
        text.config(state=tk.DISABLED)

    def show_about(self):
        """Mostra informações sobre o programa"""
        messagebox.showinfo("Sobre",
                           "Analisador TONTO\n"
                           "Versão 3.0\n\n"
                           "Analisador Léxico, Sintático e Semântico\n"
                           "para a linguagem TONTO (Textual Ontology Language)\n\n"
                           "Recursos:\n"
                           "• Análise Léxica completa\n"
                           "• Análise Sintática com PLY\n"
                           "• Validação de Padrões de Ontologias (ODPs)\n\n"
                           "Desenvolvido para a disciplina de Compiladores\n"
                           "Autores: Daniel Rocha Maia e Gabriela de Oliveira Pascoal")
