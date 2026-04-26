import re

class CodeMetrics:
    """
    A class to calculate various code metrics.
    """

    def __init__(self, code):
        self.code = code

    def calculate_lines_of_code(self):
        lines = self.code.splitlines()
        loc = len(lines)
        non_empty_loc = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
        return {"LOC": loc, "Non-Empty LOC": non_empty_loc}

    def calculate_function_points(self):
        function_points = len(re.findall(r'\bdef\b', self.code)) + len(re.findall(r'\bclass\b', self.code))
        return {"Function Points": function_points}

    def calculate_cyclomatic_complexity(self):
        decision_points = len(re.findall(r'\b(if|else if|for|while|case|catch|&&|\|\|)\b', self.code))
        nested_loops = len(re.findall(r'\b(for|while)\b.*\b(for|while)\b', self.code))
        cyclomatic_complexity = decision_points + nested_loops
        return {"Cyclomatic Complexity": cyclomatic_complexity}

    def calculate_all_metrics(self):
        loc_metrics = self.calculate_lines_of_code()
        function_points = self.calculate_function_points()
        cyclomatic_complexity = self.calculate_cyclomatic_complexity()
        return {**loc_metrics, **function_points, **cyclomatic_complexity}
