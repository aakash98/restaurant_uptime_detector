import os


class Constants:
    STATUS_DATE_DELTA = int(os.environ.get('STATUS_DATE_DELTA', 7))
    RESTAURANT_OP_TIMESLOT_FILE = (os.environ.
                                   get('RESTAURANT_OP_TIMESLOT_FILE',
                                       '~/Documents/Menu hours.csv'))
    RESTAURANT_OP_TIMESLOT_FIELDS = os.environ.get('RESTAURANT_OP_TIMESLOT_FIELDS',
                                                   ['store_id', 'day', 'start_time_local',
                                                    'end_time_local'])
    RESTAURANT_TIMEZONE_INFO_FILE = os.environ.get('RESTAURANT_TIMEZONE_INFO',
                                                   '~/Documents/bq-results-20230125-202210-1674678181880.csv')
    RESTAURANT_TIMEZONE_INFO_FIELDS = os.environ.get('RESTAURANT_TIMEZONE_INFO_FIELDS',
                                                     ['store_id', 'timezone_str'])
    RESTAURANT_STATUS_DATA_FILE = os.environ.get('RESTAURANT_STATUS_DATA_FILE',
                                                 '~/Documents/store status.csv')
    RESTAURANT_STATUS_DATA_FIELDS = os.environ.get('RESTAURANT_STATUS_DATA_FIELDS',
                                                   ['store_id', 'status', 'timestamp_utc'])
