from datetime import datetime
from typing import Dict, Optional
from restaurant_reports.models import RestaurantStatusData, ConsolidatedReport, ReportStatus
from restaurant_reports.tasks import render_restaurant_reports
from restaurant_reports.services.store_status_aggregator import StoreStatusAggregatorService
import pandas as pd


class TriggerReportService(object):

    @staticmethod
    def create_report_request(use_latest=False) -> Dict:
        # Made reference_timestamp configurable for static loading of data as well as dynamic loading
        if use_latest:
            reference_timestamp = datetime.now()
        else:
            reference_timestamp = RestaurantStatusData.objects.filter().last().timestamp
        # ConsolidatedReport Collects All Individual Store Reports And Compiles It
        consolidated_report = ConsolidatedReport.objects.create(reference_timestamp=reference_timestamp)
        # Implemented Async Queue Using Celery For Fast Processing
        render_restaurant_reports.delay(consolidated_report.pk)
        return {"success": True, "report_id": consolidated_report.pk if consolidated_report else None}

    @staticmethod
    def get_report_if_completed(report_id) -> Optional[pd.DataFrame]:
        consolidated_report = ConsolidatedReport.objects.filter(pk=report_id).first()
        if consolidated_report.status == ReportStatus.COMPLETED:
            report_data = StoreStatusAggregatorService(consolidated_report.pk).render_consolidated_report()
            return report_data
