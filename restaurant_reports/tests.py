import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.test import TestCase
from restaurant_reports.utils import ModelInjectionUtils
from restaurant_reports.models import ConsolidatedReport, RestaurantReports
from restaurant_reports.services.store_status_aggregator import StoreStatusAggregatorService
from restaurant_reports.services.trigger_report import TriggerReportService


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
        self.report = ConsolidatedReport.objects.create(reference_timestamp=datetime.date(2023, 1, 25))
        data = {"id": 1, "store_id": 1849388240019458095, "status": "completed",
                "reference_timestamp": "2023-01-25T00:00:00Z",
                "data": {"store_id": 1849388240019458095, "uptime_last_day": 17.500000000000007,
                         "uptime_last_hour": 1050.0, "uptime_last_week": 553.9206172222217, "downtime_last_day": 0,
                         "downtime_last_hour": 0, "downtime_last_week": 222.57938277777777,
                         "reference_timestamp": "20230125T00:00:00"},
                "consolidated_report": ConsolidatedReport. \
                    objects.create(reference_timestamp=datetime.datetime.now())}
        self.store_report = RestaurantReports.objects.create(**data)

    def monkey_patch_restaurant_reports(self):
        self.report.status = 'completed'
        self.report.save()
        self.store_report.consolidated_report_id = self.report.pk
        self.store_report.save()

    def test_b(self):
        # import ipdb; ipdb.set_trace()
        # Test another thing with the nominal data
        self.monkey_patch_restaurant_reports()
        report = TriggerReportService.get_report_if_completed(self.report.pk)
        assert not report.empty, f"GET Request For Report Retreival Failed"

    def test_a(self):
        # Test something with the nominal data
        # import ipdb; ipdb.set_trace()
        StoreStatusAggregatorService(self.report.pk).generate_consolidated_report()
        self.report = ConsolidatedReport.objects.get(pk=self.report.pk)
        self.store_report = RestaurantReports.objects.get(consolidated_report_id=self.report.pk)
        assert self.report.status == 'completed', f"Report Rendering Failed"
