"""
Static Analyzer Engine
Core logic for AST parsing and metric calculation
"""

import javalang
from typing import List, Dict, Any, Tuple
from detectors.base import CodeSmell
from detectors.design import DesignSmells
from detectors.implementation import ImplementationSmells
from detectors.naming_docs import NamingSmells, DocumentationSmells
from utils.helpers import count_blank_lines, count_comment_lines


class StaticAnalyzerEngine:
    """
    Main analyzer engine that orchestrates all code smell detectors
    and calculates comprehensive code metrics.
    """
    
    def __init__(self, code: str):
        """
        Initialize the analyzer engine.
        
        Args:
            code: Java source code as a string
        """
        self.code = code
        self.lines = code.split('\n')
        self.detectors: List[CodeSmell] = self._initialize_detectors()
    
    def _initialize_detectors(self) -> List[CodeSmell]:
        """
        Initialize all detector instances.
        
        Returns:
            List of code smell detector instances
        """
        return [
            DesignSmells(),
            ImplementationSmells(),
            NamingSmells(),
            DocumentationSmells()
        ]
    
    def run(self) -> Tuple[List[Dict[str, Any]], javalang.tree.CompilationUnit]:
        """
        Run the complete analysis pipeline.
        
        Returns:
            Tuple of (list of detected issues, parsed AST tree)
            
        Raises:
            ValueError: If syntax error or parsing fails
        """
        try:
            # Parse the Java source code into an AST
            tree = javalang.parse.parse(self.code)
            
            # Run all detectors
            all_issues = []
            for detector in self.detectors:
                issues = detector.detect(tree, self.lines)
                all_issues.extend(issues)
            
            return all_issues, tree
            
        except javalang.parser.JavaSyntaxError as e:
            raise ValueError(f"Syntax Error at {e.at}: {e.description}")
        except Exception as e:
            raise ValueError(f"AST Analysis Failed: {str(e)}")
    
    def calculate_metrics(self, tree: javalang.tree.CompilationUnit) -> Dict[str, Any]:
        """
        Calculate comprehensive code metrics from the AST.
        
        Args:
            tree: Parsed Java AST
            
        Returns:
            Dictionary containing various code metrics
        """
        metrics = {
            'total_classes': 0,
            'total_methods': 0,
            'total_fields': 0,
            'total_lines': len(self.lines),
            'blank_lines': count_blank_lines(self.lines),
            'comment_lines': count_comment_lines(self.lines),
            'avg_method_length': 0,
            'max_method_length': 0,
            'avg_complexity': 0,
            'max_complexity': 0,
            'code_lines': 0
        }
        
        method_lengths = []
        complexities = []
        
        # Analyze classes
        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            metrics['total_classes'] += 1
            
            # Count methods
            if node.methods:
                metrics['total_methods'] += len(node.methods)
                
                for method in node.methods:
                    # Calculate method length
                    if method.body:
                        length = len(method.body)
                        method_lengths.append(length)
                        
                        # Calculate cyclomatic complexity
                        complexity = self._calculate_complexity(method)
                        complexities.append(complexity)
            
            # Count fields
            if node.fields:
                metrics['total_fields'] += len(node.fields)
        
        # Calculate averages
        if method_lengths:
            metrics['avg_method_length'] = sum(method_lengths) / len(method_lengths)
            metrics['max_method_length'] = max(method_lengths)
        
        if complexities:
            metrics['avg_complexity'] = sum(complexities) / len(complexities)
            metrics['max_complexity'] = max(complexities)
        
        # Calculate code lines (excluding blanks and comments)
        metrics['code_lines'] = (metrics['total_lines'] - 
                                 metrics['blank_lines'] - 
                                 metrics['comment_lines'])
        
        return metrics
    
    def _calculate_complexity(self, method_node: javalang.tree.MethodDeclaration) -> int:
        """
        Calculate cyclomatic complexity for a method.
        
        Args:
            method_node: AST node representing a method
            
        Returns:
            Cyclomatic complexity value
        """
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