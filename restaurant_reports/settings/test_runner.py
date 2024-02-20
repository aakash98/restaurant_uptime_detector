import sys
from django.conf import settings
from django.test.runner import DiscoverRunner
from django.db import connection

class CustomTestRunner(DiscoverRunner):
    def setup_test_environment(self, *args, **kwargs):
        super().setup_test_environment(*args, **kwargs)
        settings.DATABASES['default']['NAME'] = 'test_database'  # Replace 'test_database' with the name of your MySQL test database

    def teardown_test_environment(self, *args, **kwargs):
        super().teardown_test_environment(*args, **kwargs)
        connection.close()

if __name__ == "__main__":
    sys.exit(CustomTestRunner().run_tests(sys.argv[1:]))
