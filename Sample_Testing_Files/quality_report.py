class QualityReport:
    """
    Generates a quality report based on code metrics.
    """

    def generate(self, metrics):
        defects_per_kloc = metrics.get("Defect Density", 0)
        maintainability_index = metrics.get("Maintainability Index", 100)  # Example default

        quality = "High" if maintainability_index > 70 and defects_per_kloc < 0.5 else "Moderate"
        if maintainability_index < 50 or defects_per_kloc >= 1:
            quality = "Low"

        return {"Quality": quality}
