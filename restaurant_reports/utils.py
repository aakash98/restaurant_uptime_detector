import pandas as pd
import numpy as np
from restaurant_reports.constants import data_map
import json
from restaurant_reports.tasks import make_an_entry


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class ModelInjectionUtils:
    @classmethod
    def make_an_entry_sync(cls, model_name, **data_fields):
        make_an_entry(model_name=model_name, **data_fields)

    @classmethod
    def make_an_entry_async(cls, model_name, **data_fields):
        make_an_entry.delay(model_name=model_name, **data_fields)


class CSVMapUtils:

    @classmethod
    def read_csv(cls, model_name='RestaurantOperationTimeSlots'):
        file_location = data_map[model_name]['file_location']
        data_frame = pd.read_csv(file_location)
        fields = data_map[model_name]['fields']
        for index in data_frame.index:
            data_fields = {field_name: data_frame.iloc[index][field_name] for field_name in fields}
            data_fields = json.loads(json.dumps(data_fields, cls=NpEncoder))
            ModelInjectionUtils.make_an_entry_sync(model_name=model_name, **data_fields)
