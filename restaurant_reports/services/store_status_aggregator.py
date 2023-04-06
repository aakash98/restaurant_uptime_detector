from restaurant_reports.models import RestaurantStatusData, ConsolidatedReport, ReportStatus, RestaurantReports
from restaurant_reports.services.report_render import ReportRenderService
from datetime import timedelta
from restaurant_reports.constants import Constants
import pandas as pd
from typing import Optional


class StoreStatusAggregatorService(object):
    report_id: int = None

    def __init__(self, report_id: int):
        self.report_id = report_id

    def generate_consolidated_report(self):
        report = ConsolidatedReport.objects.get(pk=self.report_id)
        reference_timestamp = report.reference_timestamp
        stores = set(list(RestaurantStatusData.objects.filter(
            timestamp__gte=reference_timestamp - timedelta(days=Constants.STATUS_DATE_DELTA)).values_list('store_id',
                                                                                                          flat=True)))
        number_of_stores = len(stores)
        counter = 0
        consolidated_data = []
        for store in stores:
            restaurant_report = ReportRenderService(store).get_report_by_store(self.report_id, reference_timestamp)
            if restaurant_report:
                consolidated_data.append(restaurant_report)
            print(f"Consolidating Data For {store}....Current Progress {counter*100/number_of_stores}%")
        report.status = ReportStatus.COMPLETED
        report.save()

    def render_consolidated_report(self) -> Optional[pd.DataFrame]:
        consolidated_report = ConsolidatedReport.objects.get(pk=self.report_id)
        if consolidated_report.status == ReportStatus.COMPLETED:
            reports = RestaurantReports.objects.filter(consolidated_report_id=self.report_id,
                                                       status=ReportStatus.COMPLETED)
            consolidated_report_data = [report.data for report in reports]
            consolidated_report_dataframe = pd.DataFrame(consolidated_report_data)
            return consolidated_report_dataframe
