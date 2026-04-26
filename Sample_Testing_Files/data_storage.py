class DataStorage:
    """
    A class to store and manage metric data in a decoupled manner.
    """

    def __init__(self):
        self.metrics = {}

    def save_metric(self, key, value):
        self.metrics[key] = value

    def save_metrics(self, metrics_dict):
        self.metrics.update(metrics_dict)

    def get_metrics(self):
        return self.metrics
