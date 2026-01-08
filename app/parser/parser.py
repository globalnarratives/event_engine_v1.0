"""
CIE Parser - Phase 1
Loads Lark grammar and parses CIE event strings
"""

from lark import Lark, Tree, Token
from lark.exceptions import LarkError
import os

class CIEParser:
    """Parser for Compressed Information Expression (CIE) event strings"""
    
    def __init__(self, grammar_path=None):
        """
        Initialize the CIE parser with grammar file
        
        Args:
            grammar_path: Path to .lark grammar file (defaults to grammar/cie.lark)
        """
        if grammar_path is None:
            # Default to grammar/cie.lark in same directory as this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            grammar_path = os.path.join(base_dir, 'grammar', 'cie.lark')
        
        # Load grammar file
        # with open(grammar_path, 'r', encoding='utf-8') as f:
            # grammar = f.read()
        
        # Initialize Lark parser
        self.parser = Lark.open(grammar_path, start='event', parser='lalr')
    
    def parse(self, cie_string):
        """
        Parse a CIE event string
        
        Args:
            cie_string: The CIE string to parse
            
        Returns:
            Lark Tree object if successful
            
        Raises:
            LarkError: If parsing fails
        """
        try:
            tree = self.parser.parse(cie_string)
            return tree
        except LarkError as e:
            raise ParseError(f"Failed to parse CIE string: {e}")
    
    def parse_safe(self, cie_string):
        """
        Parse a CIE string and return result with error handling
        
        Args:
            cie_string: The CIE string to parse
            
        Returns:
            dict with 'success' (bool), 'tree' (if success), 'error' (if failed)
        """
        try:
            tree = self.parse(cie_string)
            return {
                'success': True,
                'tree': tree,
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'tree': None,
                'error': str(e)
            }
    
    def pretty_print(self, tree):
        """
        Pretty print a parse tree
        
        Args:
            tree: Lark Tree object from parse()
        """
        print(tree.pretty())


class ParseError(Exception):
    """Custom exception for CIE parsing errors"""
    pass


def main():
    """
    Simple test function - parse a basic CIE string
    """
    parser = CIEParser()
    
    # Test with a simple event
    test_string = "rus.hos.exc.01 [s-st] $ usa.hos {s-pr}"
    
    print("Testing CIE Parser - Phase 1")
    print("=" * 50)
    print(f"\nInput: {test_string}\n")
    
    result = parser.parse_safe(test_string)
    
    if result['success']:
        print("✓ Parse successful!\n")
        print("Parse tree:")
        parser.pretty_print(result['tree'])
    else:
        print("✗ Parse failed!")
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()