from django.test import TestCase
from restaurant_reports.utils import ModelInjectionUtils
import json
from django.core.serializers.json import DjangoJSONEncoder

class MyTestCase(TestCase):
    def setUp(self):
        # Create a user
        with open('restaurant_reports/test_data.json') as fp:
            json_file = json.load(fp)
            json_file = json.loads(json.dumps(json_file, cls=DjangoJSONEncoder))
            for model_name, data_entries in json_file.items():
                for entry in data_entries:
                    try:
                        ModelInjectionUtils.make_an_entry_sync(model_name=model_name, **entry)
                    except:
                        continue

    def test_something(self):
        # Test something with the nominal data
        import ipdb; ipdb.set_trace()
        ...

    def test_another_thing(self):
        # Test another thing with the nominal data
        ...
