import os
import re

files_to_check = [
    'main.tex',
    'sections/00_abstract.tex',
    'sections/01_scenariet.tex',
    'sections/02_kjerneteknologi.tex',
    'sections/03_innovasjonen.tex',
    'sections/04_kildestrategi.tex',
    'sections/05_dimensjonering.tex',
    'sections/06_totalforsvar_ros.tex',
    'sections/07_konklusjon.tex',
    'sections/08_ki_erklaring.tex'
]

def check_files():
    all_labels = set()
    all_refs = []
    all_graphics = []
    errors = []

    for path in files_to_check:
        if not os.path.exists(path):
            errors.append(f"File not found: {path}")
            continue

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check matching braces
        # Strip comments
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            line_no_comment = re.sub(r'(?<!\\)%.*', '', line)
            clean_lines.append(line_no_comment)
        clean_content = '\n'.join(clean_lines)

        # Brace balance
        open_b = clean_content.count('{')
        close_b = clean_content.count('}')
        if open_b != close_b:
            errors.append(f"{path}: Mismatched curly braces {{: {open_b} vs }}: {close_b}")

        # Square brackets inside text or commands
        # Environment balance
        begins = re.findall(r'\\begin\{([^}]+)\}', clean_content)
        ends = re.findall(r'\\end\{([^}]+)\}', clean_content)
        
        # Check environments matching order
        env_stack = []
        for token in re.finditer(r'\\(begin|end)\{([^}]+)\}', clean_content):
            kind, env_name = token.group(1), token.group(2)
            if kind == 'begin':
                env_stack.append((env_name, token.start()))
            else:
                if not env_stack:
                    errors.append(f"{path}: Unexpected \\end{{{env_name}}} with no open environment")
                else:
                    last_env, _ = env_stack.pop()
                    if last_env != env_name:
                        errors.append(f"{path}: Environment mismatch: \\begin{{{last_env}}} closed with \\end{{{env_name}}}")

        if env_stack:
            for last_env, _ in env_stack:
                # If in modular files, document env is in main.tex
                if path != 'main.tex' and last_env == 'document':
                    pass
                else:
                    errors.append(f"{path}: Unclosed environment: \\begin{{{last_env}}}")

        # Collect labels and refs
        labels = re.findall(r'\\label\{([^}]+)\}', clean_content)
        for lab in labels:
            all_labels.add(lab)

        refs = re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}', clean_content)
        for r in refs:
            all_refs.append((r, path))

        # Collect graphics
        graphics = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', clean_content)
        for g in graphics:
            all_graphics.append((g, path))

    # Check unresolved refs
    for r, p in all_refs:
        if r not in all_labels:
            errors.append(f"Unresolved reference: \\ref{{{r}}} in {p}")

    # Check graphics files exist
    for g, p in all_graphics:
        # Check direct or relative
        if not os.path.exists(g):
            # Check with extension or without
            found = False
            for ext in ['', '.jpg', '.png', '.pdf']:
                if os.path.exists(g + ext):
                    found = True
                    break
            if not found:
                errors.append(f"Missing graphics file: {g} referenced in {p}")

    print("=== LATEX VALIDATION REPORT ===")
    if not errors:
        print("ALL CHECKS PASSED PERFECTLY!")
        print(f"Verified {len(files_to_check)} files.")
        print(f"All {len(all_labels)} labels resolved ({', '.join(all_labels)}).")
        print(f"All {len(all_graphics)} graphic files verified on disk.")
    else:
        print(f"FOUND {len(errors)} ISSUE(S):")
        for err in errors:
            print("  -", err)

check_files()
