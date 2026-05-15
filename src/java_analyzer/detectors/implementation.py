"""
Implementation Smell Detector
Identifies implementation-level code smells and complexity issues
"""

from typing import List, Dict, Any
import javalang
from detectors.base import CodeSmell


class ImplementationSmells(CodeSmell):
    """
    Detects implementation-level code smells including:
    - High Cyclomatic Complexity
    - Long Methods
    - Long Parameter Lists
    - Empty Catch Blocks
    - Magic Numbers
    - Deep Nesting
    """
    
    def detect(self, tree: javalang.tree.CompilationUnit, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect all implementation smells in the given AST."""
        results = []
        
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            results.extend(self._detect_high_complexity(node))
            results.extend(self._detect_long_method(node))
            results.extend(self._detect_long_parameter_list(node))
            results.extend(self._detect_empty_catch_blocks(node))
            results.extend(self._detect_magic_numbers(node))
            results.extend(self._detect_deep_nesting(node))
        
        return results
    
    def _detect_high_complexity(self, node: javalang.tree.MethodDeclaration) -> List[Dict[str, Any]]:
        """Detect methods with high cyclomatic complexity."""
        results = []
        complexity = self._calculate_complexity(node)
        
        if complexity > 10:
            results.append(self._create_issue(
                "High Complexity",
                node.name,
                "High",
                f"Cyclomatic complexity: {complexity}",
                "Implementation"
            ))
        return results
    
    def _detect_long_method(self, node: javalang.tree.MethodDeclaration) -> List[Dict[str, Any]]:
        """Detect methods that are too long."""
        results = []
        
        if node.body and len(node.body) > 30:
            results.append(self._create_issue(
                "Long Method",
                node.name,
                "Medium",
                f"Method body contains {len(node.body)} statements",
                "Implementation"
            ))
        return results
    
    def _detect_long_parameter_list(self, node: javalang.tree.MethodDeclaration) -> List[Dict[str, Any]]:
        """Detect methods with too many parameters."""
        results = []
        
        if len(node.parameters) > 5:
            results.append(self._create_issue(
                "Long Parameter List",
                node.name,
                "Low",
                f"{len(node.parameters)} parameters",
                "Implementation"
            ))
        return results
    
    def _detect_empty_catch_blocks(self, node: javalang.tree.MethodDeclaration) -> List[Dict[str, Any]]:
        """Detect empty catch blocks that swallow exceptions."""
        results = []
        
        for _, catch in node.filter(javalang.tree.CatchClause):
            if not catch.block or len(catch.block) == 0:
                results.append(self._create_issue(
                    "Empty Catch Block",
                    node.name,
                    "Critical",
                    "Exception swallowed without logs or logic",
                    "Implementation"
                ))
        return results
    
    def _detect_magic_numbers(self, node: javalang.tree.MethodDeclaration) -> List[Dict[str, Any]]:
        """Detect hard-coded numeric literals (magic numbers)."""
        results = []
        magic_count = self._count_magic_numbers(node)
        
        if magic_count > 3:
            results.append(self._create_issue(
                "Magic Numbers",
                node.name,
                "Low",
                f"{magic_count} hard-coded numeric literals found",
                "Implementation"
            ))
        return results
    
    def _detect_deep_nesting(self, node: javalang.tree.MethodDeclaration) -> List[Dict[str, Any]]:
        """Detect deeply nested control structures."""
        results = []
        max_depth = self._calculate_nesting_depth(node)
        
        if max_depth > 4:
            results.append(self._create_issue(
                "Deep Nesting",
                node.name,
                "Medium",
                f"Maximum nesting depth: {max_depth}",
                "Implementation"
            ))
        return results
    
    # Helper methods for calculations
    
    def _calculate_complexity(self, method_node: javalang.tree.MethodDeclaration) -> int:
        """Calculate cyclomatic complexity of a method."""
        count = 1
        branch_types = (
            javalang.tree.IfStatement,
            javalang.tree.WhileStatement,
            javalang.tree.DoStatement,
            javalang.tree.ForStatement,
            javalang.tree.CatchClause,
            javalang.tree.SwitchStatementCase,
            javalang.tree.TernaryExpression
        )
        
        for _, node in method_node.filter(branch_types):
            count += 1
        
        return count
    
    def _count_magic_numbers(self, method_node: javalang.tree.MethodDeclaration) -> int:
        """Count magic numbers (excluding 0, 1, -1)."""
        count = 0
        
        for _, node in method_node.filter(javalang.tree.Literal):
            if hasattr(node, 'value') and node.value:
                try:
                    val = float(node.value)
                    if val not in [0, 1, -1]:
                        count += 1
                except:
                    pass
        
        return count
    
    def _calculate_nesting_depth(self, node, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of control structures."""
        max_depth = current_depth
        nesting_constructs = (
            javalang.tree.IfStatement,
            javalang.tree.WhileStatement,
            javalang.tree.ForStatement,
            javalang.tree.DoStatement,
            javalang.tree.TryStatement
        )
        
        for child in node.children:
            if isinstance(child, nesting_constructs):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            elif hasattr(child, 'children'):
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth