"""
Abstract Base Class for Code Smell Detectors
Defines the contract that all detector implementations must follow
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import javalang


class CodeSmell(ABC):
    """
    Abstract base class for all code smell detectors.
    Implements the Strategy Pattern for different detection algorithms.
    """
    
    @abstractmethod
    def detect(self, tree: javalang.tree.CompilationUnit, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Detect code smells in the given AST tree.
        
        Args:
            tree: Parsed Java AST (Abstract Syntax Tree)
            lines: Source code split into lines
            
        Returns:
            List of dictionaries containing detected issues with keys:
            - Type: The smell type name
            - Target: The affected element (class/method name)
            - Severity: Critical/High/Medium/Low
            - Reason: Detailed explanation
            - Category: Design/Implementation/Naming/Documentation
        """
        pass
    
    def _create_issue(self, smell_type: str, target: str, severity: str, 
                      reason: str, category: str) -> Dict[str, Any]:
        """
        Helper method to create a standardized issue dictionary.
        
        Args:
            smell_type: Name of the code smell
            target: Affected code element
            severity: Severity level
            reason: Detailed explanation
            category: Issue category
            
        Returns:
            Standardized issue dictionary
        """
        return {
            "Type": smell_type,
            "Target": target,
            "Severity": severity,
            "Reason": reason,
            "Category": category
        }