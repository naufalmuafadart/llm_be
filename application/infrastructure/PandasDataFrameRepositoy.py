from application.repository.DataFrameRepository import DataFrameRepository
import pandas as pd

class PandasDataFrameRepository(DataFrameRepository):
    def get_data(self, file_name):
        return pd.read_csv(f'./dataset/{file_name}.csv')
