"""
CIE Parser Module
Provides parsing functionality for Compressed Information Expression (CIE) event strings
"""

from .parser import CIEParser, ParseError

__all__ = ['CIEParser', 'ParseError']