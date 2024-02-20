import os


class Constants:
    STATUS_DATE_DELTA = int(os.environ.get('STATUS_DATE_DELTA', 7))
    RESTAURANT_OP_TIMESLOT_FILE = (os.environ.
                                   get('RESTAURANT_OP_TIMESLOT_FILE',
                                       'restaurant_reports/file_storage/Menu hours.csv'))
    RESTAURANT_OP_TIMESLOT_FIELDS = os.environ.get('RESTAURANT_OP_TIMESLOT_FIELDS',
                                                   ['store_id', 'day', 'start_time_local',
                                                    'end_time_local'])
    RESTAURANT_TIMEZONE_INFO_FILE = os.environ.get('RESTAURANT_TIMEZONE_INFO',
                                                   'restaurant_reports/file_storage/bq-results-20230125-202210-1674678181880.csv')
    RESTAURANT_TIMEZONE_INFO_FIELDS = os.environ.get('RESTAURANT_TIMEZONE_INFO_FIELDS',
                                                     ['store_id', 'timezone_str'])
    RESTAURANT_STATUS_DATA_FILE = os.environ.get('RESTAURANT_STATUS_DATA_FILE',
                                                 'restaurant_reports/file_storage/store status.csv')
    RESTAURANT_STATUS_DATA_FIELDS = os.environ.get('RESTAURANT_STATUS_DATA_FIELDS',
                                                   ['store_id', 'status', 'timestamp_utc'])


data_map = {'RestaurantOperationTimeSlots': {'file_location': Constants.RESTAURANT_OP_TIMESLOT_FILE,
                                             'fields': Constants.RESTAURANT_OP_TIMESLOT_FIELDS},
            'RestaurantTimezoneInfo': {'file_location': Constants.RESTAURANT_TIMEZONE_INFO_FILE,
                                       'fields': Constants.RESTAURANT_TIMEZONE_INFO_FIELDS},
            'RestaurantStatusData': {'file_location': Constants.RESTAURANT_STATUS_DATA_FILE,
                                     'fields': Constants.RESTAURANT_STATUS_DATA_FIELDS}}
