"""
Ponto de entrada do Analisador TONTO
Análise Léxica e Sintática para a linguagem TONTO
"""
import tkinter as tk
from src.gui.main_window import TontoAnalyzerGUI


def main():
    """Função principal"""
    root = tk.Tk()
    app = TontoAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
