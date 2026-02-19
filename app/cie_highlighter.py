"""
CIE Syntax Highlighter
Converts plain CIE text into HTML with syntax highlighting spans
Similar to IDE code highlighting
"""

import re
from html import escape


def highlight_cie_syntax(cie_body):
    """
    Convert CIE body text to HTML with syntax highlighting.
    
    Args:
        cie_body (str): Plain text CIE body
        
    Returns:
        str: HTML with <span> tags for syntax highlighting
    """
    if not cie_body:
        return ""
    
    lines = cie_body.split('\n')
    highlighted_lines = []
    
    for line in lines:
        if not line.strip():
            highlighted_lines.append('')
            continue
            
        # Preserve leading whitespace (indentation)
        indent = len(line) - len(line.lstrip())
        leading_spaces = line[:indent]
        content = line[indent:]
        
        # Apply syntax highlighting to content
        highlighted = highlight_line(content)
        
        # Reconstruct with preserved indentation
        highlighted_lines.append(leading_spaces + highlighted)
    
    return '\n'.join(highlighted_lines)


def highlight_line(line):
    """
    Apply syntax highlighting to a single line of CIE.
    
    Highlighting rules:
    - $ symbol: cyan (cf-symbol)
    - Bullets (▪): cyan (cf-bullet)
    - Entity codes (xxx.yyy.zzz or xxx.yyy): pink (cf-entity)
    - Action codes {xxx}: yellow (cf-action)
    - Brackets []: yellow (cf-bracket)
    - Operators (/, x, \): cyan (cf-operator)
    - Relation operators (<>, >, <): green (cf-relation-op)
    - Parentheses (): white/default
    - Plain text: default
    """
    result = []
    i = 0
    
    while i < len(line):
        char = line[i]
        
        # Dollar sign
        if char == '$':
            result.append('<span class="cf-symbol">$</span>')
            i += 1
        
        # Bullet
        elif char == '▪':
            result.append('<span class="cf-bullet">▪</span>')
            i += 1
        
        # Action codes or brackets
        elif char == '{' or char == '[':
            # Find closing bracket
            close_char = '}' if char == '{' else ']'
            end = line.find(close_char, i)
            
            if end != -1:
                content = line[i:end+1]
                if char == '{':
                    result.append(f'<span class="cf-action">{escape(content)}</span>')
                else:
                    result.append(f'<span class="cf-bracket">{escape(content)}</span>')
                i = end + 1
            else:
                result.append(escape(char))
                i += 1
        
        # Operators
        elif char in ['/', '\\', 'x', 'X']:
            # Check if 'x' is part of a word or standalone operator
            if char in ['x', 'X']:
                # Check context - if surrounded by spaces or at boundaries, it's an operator
                prev_space = i == 0 or line[i-1].isspace()
                next_space = i == len(line)-1 or line[i+1].isspace()
                
                if prev_space and next_space:
                    result.append(f'<span class="cf-operator">{char}</span>')
                    i += 1
                else:
                    # Part of a word, continue to entity/text handling
                    i = handle_entity_or_text(line, i, result)
            else:
                result.append(f'<span class="cf-operator">{char}</span>')
                i += 1
        
        # Relation operators
        elif char in ['<', '>']:
            # Check for <> or standalone < >
            if char == '<' and i+1 < len(line) and line[i+1] == '>':
                result.append('<span class="cf-relation-op">&lt;&gt;</span>')
                i += 2
            else:
                result.append(f'<span class="cf-relation-op">{escape(char)}</span>')
                i += 1
        
        # Entity codes (xxx.yyy.zzz or xxx.yyy)
        elif char.isalpha() or char.isdigit():
            i = handle_entity_or_text(line, i, result)

        elif char == '@':
            result.append('<span class="cf-location-op">@</span>')
            i += 1
                
        # Whitespace and other characters
        else:
            result.append(escape(char))
            i += 1
    
    return ''.join(result)


def handle_entity_or_text(line, start, result):
    """
    Handle entity codes (xxx.yyy.zzz) or plain text.
    Returns the new index position.
    """
    i = start
    token = []
    
    # Collect alphanumeric characters and dots
    while i < len(line) and (line[i].isalnum() or line[i] in ['.', '-']):
        token.append(line[i])
        i += 1
    
    token_str = ''.join(token)
    
    # Check if it's an entity code (has at least one dot)
    if '.' in token_str:
        parts = token_str.split('.')
        if len(parts) >= 2 and all(part.isalnum() for part in parts):
            result.append(f'<span class="cf-entity">{escape(token_str)}</span>')
        else:
            result.append(escape(token_str))
    # Check if it's a 3-letter code (country code or institution)
    elif len(token_str) == 3 and token_str.isalpha() and token_str.islower():
        result.append(f'<span class="cf-country">{escape(token_str)}</span>')
    else:
        # Plain text/word
        result.append(escape(token_str))
        
    return i


# Example usage and test
if __name__ == '__main__':
    test_cie = """$ usa.hos {s-pr} / rus<>ukr
▪ {s-st} rus.hos x [rv] {s-pr}
  ▪ [s-gp] $ {s-sp} usa.hos, ukr.hos"""
    
    highlighted = highlight_cie_syntax(test_cie)
    print(highlighted)