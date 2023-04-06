from celery import shared_task
from restaurant_reports.services.store_status_aggregator import StoreStatusAggregatorService


@shared_task
def render_restaurant_reports(report_id: int):
    StoreStatusAggregatorService(report_id).generate_consolidated_report()
