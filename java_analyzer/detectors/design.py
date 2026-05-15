"""
Design Smell Detector
Identifies architectural and design-level code smells
"""

from typing import List, Dict, Any
import javalang
from detectors.base import CodeSmell


class DesignSmells(CodeSmell):
    """
    Detects design-level code smells including:
    - God Class
    - Swiss Army Knife
    - Data Class
    - Feature Envy
    - Lazy Class
    - Abstract Without Abstracts
    """
    
    def detect(self, tree: javalang.tree.CompilationUnit, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect all design smells in the given AST."""
        results = []
        
        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            results.extend(self._detect_swiss_army_knife(node))
            results.extend(self._detect_god_class(node))
            results.extend(self._detect_data_class(node))
            results.extend(self._detect_feature_envy(node))
            results.extend(self._detect_lazy_class(node))
            results.extend(self._detect_abstract_without_abstracts(node))
        
        return results
    
    def _detect_swiss_army_knife(self, node: javalang.tree.ClassDeclaration) -> List[Dict[str, Any]]:
        """Detect classes implementing too many interfaces."""
        results = []
        if node.implements and len(node.implements) > 5:
            results.append(self._create_issue(
                "Swiss Army Knife", 
                node.name, 
                "Medium", 
                f"{len(node.implements)} interfaces implemented",
                "Design"
            ))
        return results
    
    def _detect_god_class(self, node: javalang.tree.ClassDeclaration) -> List[Dict[str, Any]]:
        """Detect classes with too many methods or fields."""
        results = []
        methods = node.methods if node.methods else []
        fields = node.fields if node.fields else []
        
        if len(methods) > 20 or len(fields) > 15:
            results.append(self._create_issue(
                "God Class",
                node.name,
                "Critical",
                f"{len(methods)} methods, {len(fields)} fields",
                "Design"
            ))
        return results
    
    def _detect_data_class(self, node: javalang.tree.ClassDeclaration) -> List[Dict[str, Any]]:
        """Detect classes with no behavioral logic (only getters/setters)."""
        results = []
        methods = node.methods if node.methods else []
        
        if len(methods) > 0:
            logic_methods = [m for m in methods if not m.name.startswith(('get', 'set', 'is'))]
            if len(logic_methods) == 0:
                results.append(self._create_issue(
                    "Data Class",
                    node.name,
                    "Low",
                    "No behavioral logic found",
                    "Design"
                ))
        return results
    
    def _detect_feature_envy(self, node: javalang.tree.ClassDeclaration) -> List[Dict[str, Any]]:
        """Detect methods with excessive external method calls."""
        results = []
        methods = node.methods if node.methods else []
        
        for method in methods:
            if method.body:
                external_calls = sum(1 for _, _ in method.filter(javalang.tree.MethodInvocation))
                if external_calls > 10:
                    results.append(self._create_issue(
                        "Feature Envy",
                        f"{node.name}.{method.name}",
                        "Medium",
                        f"{external_calls} external method calls",
                        "Design"
                    ))
        return results
    
    def _detect_lazy_class(self, node: javalang.tree.ClassDeclaration) -> List[Dict[str, Any]]:
        """Detect classes with minimal functionality."""
        results = []
        methods = node.methods if node.methods else []
        fields = node.fields if node.fields else []
        
        if len(methods) < 3 and len(fields) < 3 and len(methods) > 0:
            results.append(self._create_issue(
                "Lazy Class",
                node.name,
                "Low",
                f"Minimal functionality: {len(methods)} methods, {len(fields)} fields",
                "Design"
            ))
        return results
    
    def _detect_abstract_without_abstracts(self, node: javalang.tree.ClassDeclaration) -> List[Dict[str, Any]]:
        """Detect abstract classes with no abstract methods."""
        results = []
        methods = node.methods if node.methods else []
        
        if 'abstract' in (node.modifiers or []):
            abstract_methods = [m for m in methods if 'abstract' in (m.modifiers or [])]
            if len(abstract_methods) == 0:
                results.append(self._create_issue(
                    "Abstract Without Abstracts",
                    node.name,
                    "Low",
                    "Abstract class with no abstract methods",
                    "Design"
                ))
        return results