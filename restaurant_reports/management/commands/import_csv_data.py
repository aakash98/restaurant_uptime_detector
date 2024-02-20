from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Import From CSV To DB'

    def add_arguments(self, parser):
        pass

    def go(self):
        pass

    def __call__(self, value):
        pass

    def read_csv(self, model_name):
        from restaurant_reports.utils import CSVMapUtils
        CSVMapUtils.read_csv(model_name=model_name)

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
