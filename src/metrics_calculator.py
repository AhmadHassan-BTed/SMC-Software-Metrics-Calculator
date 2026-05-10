import ast
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

@dataclass
class CodeMetrics:
    lines_of_code: int
    functions: int
    classes: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    function_points: float
    defect_density: float

def calculate_cognitive_complexity(node, complexity=0, nesting=0):
    if isinstance(node, (ast.If, ast.While, ast.For)):
        complexity += (1 + nesting)
        nesting += 1
    elif isinstance(node, ast.Try):
        complexity += (1 + nesting)

    for child in ast.iter_child_nodes(node):
        complexity = calculate_cognitive_complexity(child, complexity, nesting)

    return complexity

def calculate_function_points(metrics: CodeMetrics) -> float:
    return (metrics.functions * 3 + metrics.classes * 5) * 0.7

def analyze_python_file(file_content: str) -> Optional[CodeMetrics]:
    try:
        tree = ast.parse(file_content)

        loc = len(file_content.splitlines())
        functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])

        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1

        cognitive = calculate_cognitive_complexity(tree)

        metrics = CodeMetrics(
            lines_of_code=loc,
            functions=functions,
            classes=classes,
            cyclomatic_complexity=complexity,
            cognitive_complexity=cognitive,
            function_points=0,
            defect_density=0
        )

        metrics.function_points = calculate_function_points(metrics)
        metrics.defect_density = (complexity * cognitive) / (loc if loc > 0 else 1)

        return metrics
    except Exception:
        return None

def calculate_cocomo(kloc: float) -> Dict[str, float]:
    if kloc == 0:
        return {'effort': 0, 'time': 0, 'staff': 0}
        
    effort = 2.4 * (kloc ** 1.05)
    time = 2.5 * (effort ** 0.38)
    staff = effort / time if time > 0 else 0
    return {
        'effort': round(effort, 2),
        'time': round(time, 2),
        'staff': round(staff, 2)
    }

def analyze_agile_metrics(sprint_data: pd.DataFrame) -> Dict[str, float]:
    if sprint_data.empty:
        return {}

    velocity = sprint_data['completed_points'].mean() if 'completed_points' in sprint_data.columns else 0
    
    planned_sum = sprint_data['planned_points'].sum()
    scope_creep = ((sprint_data['added_points'].sum() / planned_sum) * 100
                   if 'added_points' in sprint_data.columns and 'planned_points' in sprint_data.columns and planned_sum > 0 else 0)

    return {
        'average_velocity': round(velocity, 2),
        'scope_creep_percentage': round(scope_creep, 2)
    }
