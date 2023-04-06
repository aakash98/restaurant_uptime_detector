import os


class Constants:
    STATUS_DATE_DELTA = int(os.environ.get('STATUS_DATE_DELTA', 7))
