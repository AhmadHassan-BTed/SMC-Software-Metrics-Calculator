class ProjectHealthReport:
    """
    Generates a project health report based on multiple reports.
    """

    def generate(self, reports):
        quality = reports.get("Quality", "Moderate")
        effort = reports.get("Effort (Hours)", 0)
        complexity = reports.get("Complexity", "Moderate")

        if quality == "High" and complexity == "Low" and effort < 50:
            health = "Excellent"
        elif quality == "Moderate" or complexity == "Moderate" or effort < 100:
            health = "Good"
        else:
            health = "Poor"

        return {"Project Health": health}
