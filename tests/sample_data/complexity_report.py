class ComplexityReport:
    """
    Generates a complexity report based on code metrics.
    """

    def generate(self, metrics):
        cyclomatic_complexity = metrics.get("Cyclomatic Complexity", 0)
        cognitive_complexity = metrics.get("Cognitive Complexity", 0)

        complexity = "High" if cyclomatic_complexity > 10 or cognitive_complexity > 15 else "Moderate"
        if cyclomatic_complexity < 5 and cognitive_complexity < 7:
            complexity = "Low"

        return {"Complexity": complexity}
