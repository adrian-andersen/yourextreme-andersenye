import os
import re

sections_to_count = [
    'sections/00_abstract.tex',
    'sections/01_scenariet.tex',
    'sections/02_kjerneteknologi.tex',
    'sections/03_innovasjonen.tex',
    'sections/04_kildestrategi.tex',
    'sections/05_dimensjonering.tex',
    'sections/06_totalforsvar_ros.tex',
    'sections/07_konklusjon.tex'
]

def clean_latex(text):
    # Remove comments
    text = re.sub(r'%.*', '', text)
    # Remove figure and table environments (captions, table bodies)
    text = re.sub(r'\\begin\{(figure|table)\*?\}[\s\S]*?\\end\{\1\*?\}', '', text)
    # Remove display math \[ ... \]
    text = re.sub(r'\\\[[\s\S]*?\\\]', '', text)
    # Remove equation/align environments
    text = re.sub(r'\\begin\{(equation|align)\*?\}[\s\S]*?\\end\{\1\*?\}', '', text)
    # Remove inline math $ ... $
    text = re.sub(r'\$[^\$]*?\$', '', text)
    # Replace \SI{val}{unit} with val
    text = re.sub(r'\\SI\{([^}]+)\}\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\num\{([^}]+)\}', r'\1', text)
    # Remove section commands but keep section title text
    text = re.sub(r'\\(section|subsection|subsubsection)\*?\{([^}]+)\}', r'\2', text)
    # Remove basic markup wrappers like \textbf{text} -> text
    for _ in range(3):
        text = re.sub(r'\\(textbf|textit|textsc|textsf|text)\{([^}]*)\}', r'\2', text)
    # Remove \begin{...} and \end{...}
    text = re.sub(r'\\(begin|end)\{[^}]*\}', '', text)
    # Remove any other LaTeX commands \command or \command[opt]{arg}
    text = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{[^}]*\})?', ' ', text)
    # Remove stray backslashes, braces, punctuation
    text = re.sub(r'[{}\\~]', ' ', text)
    words = [w for w in text.split() if w.strip()]
    return words

total_words = 0
print("=== WORD COUNT DETAILS ===")
for sec in sections_to_count:
    if os.path.exists(sec):
        with open(sec, 'r', encoding='utf-8') as f:
            raw = f.read()
        words = clean_latex(raw)
        count = len(words)
        total_words += count
        print(f"{sec:32}: {count:4d} ord")

print("-" * 45)
print(f"TOTAL BRØDTEKST (00 - 07)       : {total_words:4d} ord (Maks: 2500)")

# Check 08_ki_erklaring.tex
if os.path.exists('sections/08_ki_erklaring.tex'):
    with open('sections/08_ki_erklaring.tex', 'r', encoding='utf-8') as f:
        ki_words = clean_latex(f.read())
    print(f"sections/08_ki_erklaring.tex    : {len(ki_words):4d} ord (Ekskludert)")
