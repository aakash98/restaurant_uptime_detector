import pandas as pd
from django.core.management.base import BaseCommand
from restaurant_reports.tasks import make_an_entry
from restaurant_reports.constants import Constants

import json
import numpy as np


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


data_map = {'RestaurantOperationTimeSlots': {'file_location': Constants.RESTAURANT_OP_TIMESLOT_FILE,
                                             'fields': Constants.RESTAURANT_OP_TIMESLOT_FIELDS},
            'RestaurantTimezoneInfo': {'file_location': Constants.RESTAURANT_TIMEZONE_INFO_FILE,
                                       'fields': Constants.RESTAURANT_TIMEZONE_INFO_FIELDS},
            'RestaurantStatusData': {'file_location': Constants.RESTAURANT_STATUS_DATA_FILE,
                                     'fields': Constants.RESTAURANT_STATUS_DATA_FIELDS}}


class Command(BaseCommand):
    help = 'Import From CSV To DB'

    def add_arguments(self, parser):
        pass

    def go(self):
        pass

    def __call__(self, value):
        pass

    def read_csv(self, model_name='RestaurantOperationTimeSlots'):
        file_location = data_map[model_name]['file_location']
        data_frame = pd.read_csv(file_location)
        fields = data_map[model_name]['fields']
        for index in data_frame.index:
            data_fields = {field_name: data_frame.iloc[index][field_name] for field_name in fields}
            data_fields = json.loads(json.dumps(data_fields, cls=NpEncoder))
            make_an_entry.delay(model_name=model_name, **data_fields)

    # def import_menu_hours_data(self):
    #     restaurant_operation_time_slots = pd.read_csv('~/Documents/Menu hours.csv')
    #     for index in restaurant_operation_time_slots.index:
    #         store_id = restaurant_operation_time_slots.iloc[index]['store_id']
    #         day = restaurant_operation_time_slots.iloc[index]['day']
    #         start_time_local = restaurant_operation_time_slots.iloc[index]['start_time_local']
    #         end_time_local = restaurant_operation_time_slots.iloc[index]['end_time_local']
    #         make_an_entry.delay(model_name='RestaurantOperationTimeSlots', store_id=store_id,
    #                             day=day, start_time_local=start_time_local,
    #                             end_time_local=end_time_local)

    # def import_restaurant_timezone_info(self):
    #     restaurant_timezone_info = pd.read_csv('~/Documents/bq-results-20230125-202210-1674678181880.csv')
    #     for index in restaurant_timezone_info.index:
    #         store_id = restaurant_timezone_info.iloc[index]['store_id']
    #         timezone_str = restaurant_timezone_info.iloc[index]['timezone_str']
    #         make_an_entry.delay(model_name='RestaurantTimezoneInfo', store_id=store_id, timezone_str=timezone_str)

    # def import_restaurant_status_data(self):
    #     restaurant_status_data = pd.read_csv('~/Documents/store status.csv')
    #     for index in restaurant_status_data.index:
    #         store_id = restaurant_status_data.iloc[index]['store_id']
    #         status = restaurant_status_data.iloc[index]['status']
    #         timestamp_utc = restaurant_status_data.iloc[index]['timestamp_utc']
    #         make_an_entry.delay(model_name='RestaurantStatusData', store_id=store_id, status=status,
    #                             timestamp_utc=timestamp_utc)

    def handle(self, *args, **kwargs):
        try:
            print(f"Importing Restaurant Timezone Mapping.....")
            self.read_csv(model_name='RestaurantTimezoneInfo')
        except Exception as ex:
            print(f"Importing Restaurant Timezone Mapping Failed {ex}")
            return
        try:
            print(f"Importing Restaurant Menu Hour Mapping.....")
            self.read_csv(model_name='RestaurantOperationTimeSlots')
        except Exception as ex:
            print(f"Importing Restaurant Menu Hour Mapping Failed {ex}")
            return
        try:
            print(f"Importing Restaurant Status Mapping.....")
            self.read_csv(model_name='RestaurantStatusData')
        except Exception as ex:
            print(f"Importing Restaurant Status Mapping Failed {ex}")
            return
