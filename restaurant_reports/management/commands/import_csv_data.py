import pandas as pd
from datetime import datetime
import pytz
from restaurant_reports.models import RestaurantStatusData, RestaurantTimezoneInfo, RestaurantOperationTimeSlots
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Import From CSV To DB'

    def add_arguments(self, parser):
        pass

    def go(self):
        pass

    def __call__(self, value):
        pass

    def import_menu_hours_data(self):
        restaurant_operation_time_slots = pd.read_csv('Menu hours.csv')
        for index in restaurant_operation_time_slots.index:
            store_id = restaurant_operation_time_slots.iloc[index]['store_id']
            day_of_week = restaurant_operation_time_slots.iloc[index]['day']
            timezone_data = RestaurantTimezoneInfo.objects.filter(store_id=store_id).last()
            timezone = timezone_data.timezone if timezone_data else 'America/Chicago'
            start_time_local = datetime.strptime(restaurant_operation_time_slots.iloc[index]['start_time_local'],
                                                 '%H:%M:%S').time().replace(tzinfo=pytz.timezone(timezone))
            end_time_local = datetime.strptime(restaurant_operation_time_slots.iloc[index]['end_time_local'],
                                               '%H:%M:%S').time().replace(tzinfo=pytz.timezone(timezone))
            RestaurantOperationTimeSlots.objects.create(store_id=store_id, start_time=start_time_local,
                                                        end_time=end_time_local, day_of_week=day_of_week)

    def import_restaurant_timezone_info(self):
        restaurant_timezone_info = pd.read_csv('bq-results-20230125-202210-1674678181880.csv')
        for index in restaurant_timezone_info.index:
            store_id = restaurant_timezone_info.iloc[index]['store_id']
            timezone = restaurant_timezone_info.iloc[index]['timezone_str']
            RestaurantTimezoneInfo.objects.create(store_id=store_id, timezone=timezone)

    def import_restaurant_status_data(self):
        restaurant_status_data = pd.read_csv('store status.csv')

        for index in restaurant_status_data.index:
            store_id = restaurant_status_data.iloc[index]['store_id']
            status = restaurant_status_data.iloc[index]['status']
            try:
                timestamp = datetime.strptime(restaurant_status_data.iloc[index]['timestamp_utc'],
                                              "%Y-%m-%d %H:%M:%S.%f UTC").replace(tzinfo=pytz.UTC)
            except Exception as ex:
                print(ex)
                timestamp = datetime.strptime(restaurant_status_data.iloc[index]['timestamp_utc'],
                                              "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=pytz.UTC)
            restaurant_status_datapoint = RestaurantStatusData.objects.create(store_id=store_id,
                                                status=status,
                                                timestamp=timestamp)

    def handle(self, *args, **kwargs):
        try:
            print(f"Importing Restaurant Timezone Mapping.....")
            self.import_restaurant_timezone_info()
        except Exception as ex:
            print(f"Importing Restaurant Timezone Mapping Failed {ex}")
            return
        try:
            print(f"Importing Restaurant Menu Hour Mapping.....")
            self.import_menu_hours_data()
        except Exception as ex:
            print(f"Importing Restaurant Menu Hour Mapping Failed {ex}")
            return
        try:
            print(f"Importing Restaurant Status Mapping.....")
            self.import_restaurant_status_data()
        except Exception as ex:
            print(f"Importing Restaurant Status Mapping Failed {ex}")
            return
