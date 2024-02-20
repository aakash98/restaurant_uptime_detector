from django.db import models
from django.db.models.query import QuerySet
from typing import Optional, Union, List
from datetime import datetime, timedelta
from restaurant_reports.constants import Constants


class RestaurantStatus(object):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHOICES = (
        (ACTIVE, ACTIVE),
        (INACTIVE, INACTIVE),
    )


class ReportStatus(object):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"
    CHOICES = (
        (IN_PROGRESS, IN_PROGRESS),
        (COMPLETED, COMPLETED),
        (FAILED, FAILED),
        (ABORTED, ABORTED),
    )


class RestaurantStatusData(models.Model):
    store_id = models.BigIntegerField(null=False, db_index=True)
    status = models.CharField(null=False, choices=RestaurantStatus.CHOICES, max_length=64)
    timestamp_utc = models.DateTimeField(null=False)

    @staticmethod
    def get_store_status_with_reference(store_id: int, reference_timestamp: Optional[datetime]) -> Union[
        QuerySet, List]:
        if not reference_timestamp:
            reference_timestamp = datetime.now()
        restaurant_status_records = RestaurantStatusData.objects.filter(store_id=store_id,
                                                                        timestamp_utc__gte=reference_timestamp - timedelta(
                                                                            days=Constants.STATUS_DATE_DELTA))
        return restaurant_status_records


class RestaurantOperationTimeSlots(models.Model):
    store_id = models.BigIntegerField(null=False, db_index=True)
    day = models.IntegerField(default=0, null=False)
    start_time_local = models.TimeField(null=False)
    end_time_local = models.TimeField(null=False)


class RestaurantTimezoneInfo(models.Model):
    store_id = models.BigIntegerField(null=False, db_index=True)
    timezone_str = models.CharField(null=False, max_length=64)


class ConsolidatedReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    reference_timestamp = models.DateTimeField(null=False)
    status = models.CharField(choices=ReportStatus.CHOICES, default=ReportStatus.IN_PROGRESS, max_length=64,
                              null=False, blank=False)


class RestaurantReports(models.Model):
    store_id = models.BigIntegerField(null=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    status = models.CharField(choices=ReportStatus.CHOICES, default=ReportStatus.IN_PROGRESS, max_length=64,
                              null=False, blank=False)
    reference_timestamp = models.DateTimeField(null=False)
    data = models.JSONField(null=True, blank=True)
    consolidated_report = models.ForeignKey(ConsolidatedReport, null=False, blank=False, on_delete=models.CASCADE, )


model_factory = {'RestaurantStatusData': RestaurantStatusData,
                 'RestaurantOperationTimeSlots': RestaurantOperationTimeSlots,
                 'RestaurantTimezoneInfo': RestaurantTimezoneInfo}
