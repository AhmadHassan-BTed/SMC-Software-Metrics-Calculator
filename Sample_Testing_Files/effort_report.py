class EffortReport:
    """
    Generates an effort report based on code metrics.
    """

    def generate(self, metrics):
        loc = metrics.get("LOC", 0)
        cyclomatic_complexity = metrics.get("Cyclomatic Complexity", 0)
        function_points = metrics.get("Function Points", 1)

        effort = loc + (cyclomatic_complexity * 2) + (function_points * 3)  # Example formula
        return {"Effort (Hours)": effort}
