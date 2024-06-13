import pandas as pd

class DataProcessor:
    def __init__(self, data):
        self.data = data

    def apply_filters(self, filters)-> pd.DataFrame:
        filtered_data = self.data
        for filter_func in filters:
            filtered_data = filter_func(filtered_data)
        return filtered_data
