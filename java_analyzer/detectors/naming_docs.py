"""
Naming Convention and Documentation Smell Detectors
Validates naming standards and documentation coverage
"""

from typing import List, Dict, Any
import javalang
from detectors.base import CodeSmell
from utils.helpers import validate_class_name, validate_method_name


class NamingSmells(CodeSmell):
    """
    Detects naming convention violations including:
    - Invalid class names (PascalCase)
    - Invalid method names (camelCase)
    - Short identifiers
    """
    
    def detect(self, tree: javalang.tree.CompilationUnit, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect all naming convention violations."""
        results = []
        
        # Check class naming conventions
        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            if not validate_class_name(node.name):
                results.append(self._create_issue(
                    "Invalid Class Name",
                    node.name,
                    "Low",
                    "Class name should follow PascalCase convention",
                    "Naming"
                ))
            
            if len(node.name) < 3:
                results.append(self._create_issue(
                    "Short Name",
                    node.name,
                    "Low",
                    "Class name too short (< 3 characters)",
                    "Naming"
                ))
        
        # Check method naming conventions
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            if not validate_method_name(node.name):
                results.append(self._create_issue(
                    "Invalid Method Name",
                    node.name,
                    "Low",
                    "Method name should follow camelCase convention",
                    "Naming"
                ))
            
            # Allow short common method names
            if len(node.name) < 3 and node.name not in ['is', 'do', 'to', 'of']:
                results.append(self._create_issue(
                    "Short Name",
                    node.name,
                    "Low",
                    "Method name too short (< 3 characters)",
                    "Naming"
                ))
        
        return results


class DocumentationSmells(CodeSmell):
    """
    Detects missing or inadequate documentation including:
    - Missing class Javadoc
    - Missing public method Javadoc
    """
    
    def detect(self, tree: javalang.tree.CompilationUnit, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect all documentation issues."""
        results = []
        
        # Check class documentation
        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            if not node.documentation:
                results.append(self._create_issue(
                    "Missing Class Documentation",
                    node.name,
                    "Low",
                    "No Javadoc found for class",
                    "Documentation"
                ))
        
        # Check public method documentation
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            if 'public' in (node.modifiers or []) and not node.documentation:
                results.append(self._create_issue(
                    "Missing Method Documentation",
                    node.name,
                    "Low",
                    "No Javadoc found for public method",
                    "Documentation"
                ))
        
        return results