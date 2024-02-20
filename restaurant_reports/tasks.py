from celery import shared_task
from restaurant_reports.services.store_status_aggregator import StoreStatusAggregatorService
from datetime import datetime
import pytz
from restaurant_reports.models import model_factory


@shared_task
def render_restaurant_reports(report_id: int):
    StoreStatusAggregatorService(report_id).generate_consolidated_report()




@shared_task
def make_an_entry(model_name='RestaurantStatusData', **kwargs):
    if model_name == 'RestaurantStatusData':
        try:
            timestamp_utc = kwargs['timestamp_utc']
            timestamp_utc = datetime.strptime(timestamp_utc,
                              "%Y-%m-%d %H:%M:%S.%f UTC").replace(tzinfo=pytz.UTC)
        except Exception as ex:
            print(ex)
            try:
                timestamp_utc = datetime.strptime(kwargs['timestamp_utc'],
                                              "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=pytz.UTC)
            except Exception as ex:
                print(ex)
                timestamp_utc = datetime.strptime(kwargs['timestamp_utc'],
                                                   "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
        kwargs['timestamp_utc'] = timestamp_utc
    elif model_name == 'RestaurantOperationTimeSlots':
        start_time_local = kwargs['start_time_local']
        end_time_local = kwargs['end_time_local']
        store_id = kwargs['store_id']
        timezone_data = model_factory['RestaurantTimezoneInfo'].objects.filter(store_id=store_id).last()
        timezone = timezone_data.timezone_str if timezone_data else 'America/Chicago'
        start_time_local = datetime.strptime(start_time_local,
                                             '%H:%M:%S').time().replace(tzinfo=pytz.timezone(timezone))
        end_time_local = datetime.strptime(end_time_local,
                                           '%H:%M:%S').time().replace(tzinfo=pytz.timezone(timezone))
        kwargs['start_time_local'] = start_time_local
        kwargs['end_time_local'] = end_time_local
    print(kwargs)
    model_factory[model_name].objects.create(**kwargs)
