from restaurant_reports.models import RestaurantStatusData, RestaurantReports, ReportStatus, \
    RestaurantOperationTimeSlots, RestaurantTimezoneInfo
from typing import Optional, Dict
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
import pytz
import json


class ReportRenderService(object):
    store_id: int = None
    uptime_last_hour: Optional[int] = 0
    uptime_last_day: Optional[int] = 0
    uptime_last_week: Optional[int] = 0
    downtime_last_hour: Optional[int] = 0
    downtime_last_day: Optional[int] = 0
    downtime_last_week: Optional[int] = 0

    def __init__(self, store_id):
        self.store_id = store_id

    def compute_restaurant_status_in_intervals(self, time_intervals, available_period, restaurant_status_checks,
                                               mode='hour', computation='week'):
        if mode == 'minute':
            seconds_unit_conversion_denominator = 60
        else:
            seconds_unit_conversion_denominator = 3600
        for time_interval, available_period_in_interval in zip(time_intervals, available_period):
            if available_period_in_interval > 0:
                interval_start, interval_end = time_interval
                interval_start_utc, interval_end_utc = interval_start.astimezone(tz=pytz.UTC), interval_end.astimezone(
                    tz=pytz.UTC)
                status_checks_in_interval = restaurant_status_checks.filter(timestamp__gt=interval_start_utc,
                                                                            timestamp__lt=interval_end_utc)
                mini_interval_start = interval_start_utc
                for status_check in status_checks_in_interval:
                    period_in_mini_interval = (
                                                      status_check.timestamp_utc - mini_interval_start).total_seconds() / seconds_unit_conversion_denominator
                    available_period_in_interval -= period_in_mini_interval
                    mini_interval_start = status_check.timestamp_utc
                    if status_check.status == 'active':
                        if mode == 'minute':
                            self.uptime_last_hour += period_in_mini_interval
                        elif mode == 'hour' and computation == 'day':
                            self.uptime_last_day += period_in_mini_interval
                        else:
                            self.uptime_last_week += period_in_mini_interval
                    else:
                        if mode == 'minute':
                            self.downtime_last_hour += period_in_mini_interval
                        elif mode == 'hour' and computation == 'day':
                            self.downtime_last_day += period_in_mini_interval
                        else:
                            self.downtime_last_week += period_in_mini_interval
                if status_checks_in_interval.last():
                    period_in_mini_interval = ((
                                                       interval_end_utc - status_checks_in_interval.last().timestamp_utc).total_seconds()) / seconds_unit_conversion_denominator
                    if status_checks_in_interval.last().status == 'active':
                        if mode == 'minute':
                            self.uptime_last_hour += period_in_mini_interval
                        elif mode == 'hour' and computation == 'day':
                            self.uptime_last_day += period_in_mini_interval
                        else:
                            self.uptime_last_week += period_in_mini_interval
                    else:
                        if mode == 'minute':
                            self.downtime_last_hour += period_in_mini_interval
                        elif mode == 'hour' and computation == 'day':
                            self.downtime_last_day += period_in_mini_interval
                        else:
                            self.downtime_last_week += period_in_mini_interval

    def compute_hourly_stats(self, reference_timestamp, restaurant_status_checks):
        restaurant_timezone = RestaurantTimezoneInfo.objects.filter(store_id=self.store_id).last()
        if not restaurant_timezone:
            restaurant_timezone = 'America/Chicago'
        else:
            restaurant_timezone = restaurant_timezone.timezone_str

        # Convert TimeSlots Into Local TimzeZone
        query_time_window_end = reference_timestamp.astimezone(pytz.timezone(restaurant_timezone))
        query_time_window_start = query_time_window_end - timedelta(days=1)
        day_of_week_end = query_time_window_end.weekday()
        day_of_week_start = query_time_window_start.weekday()

        # There Will Be Cases Where Our Requested Relative Period lies between 2 dates
        restaurant_operational_hours_start = RestaurantOperationTimeSlots.objects.filter(store_id=self.store_id,
                                                                                         day=day_of_week_start).last()
        restaurant_operational_hours_end = RestaurantOperationTimeSlots.objects.filter(store_id=self.store_id,
                                                                                       day=day_of_week_end).last()
        if restaurant_operational_hours_start or restaurant_operational_hours_end:
            # Case When Requested Time Period Falls In The Same Day
            operational_hours_start_phase_1 = datetime.combine(query_time_window_start.date(),
                                                               restaurant_operational_hours_start.start_time_local).replace(
                tzinfo=pytz.UTC) if restaurant_operational_hours_start else None
            operational_hours_end_phase_1 = datetime.combine(query_time_window_start.date(),
                                                             restaurant_operational_hours_start.end_time_local).replace(
                tzinfo=pytz.UTC) if restaurant_operational_hours_start else None
            operational_hours_start_phase_2 = datetime.combine(query_time_window_end.date(),
                                                               restaurant_operational_hours_end.start_time_local).replace(
                tzinfo=pytz.UTC) if restaurant_operational_hours_end else None
            operational_hours_end_phase_2 = datetime.combine(query_time_window_end.date(),
                                                             restaurant_operational_hours_end.end_time_local).replace(
                tzinfo=pytz.UTC) if restaurant_operational_hours_end else None

            # Abort Further Operations If Restaurant Does Not Operate On A Particular Weekday

            if operational_hours_start_phase_1:
                window_start_time_phase_1 = operational_hours_start_phase_1 if operational_hours_start_phase_1 > query_time_window_start else query_time_window_start
            else:
                window_start_time_phase_1 = None

            if operational_hours_end_phase_1:
                window_end_time_phase_1 = operational_hours_end_phase_1 if operational_hours_end_phase_1 < query_time_window_end else query_time_window_end
            else:
                window_end_time_phase_1 = None

            if operational_hours_start_phase_2:
                window_start_time_phase_2 = operational_hours_start_phase_2 if operational_hours_start_phase_2 > query_time_window_start else query_time_window_start
            else:
                window_start_time_phase_2 = None

            if operational_hours_end_phase_2:
                window_end_time_phase_2 = operational_hours_end_phase_2 if operational_hours_end_phase_2 < query_time_window_end else query_time_window_end
            else:
                window_end_time_phase_2 = None

            # Designate Time Intervals According To QueryTime, RestaurantSchedules, Store
            time_intervals = []
            available_minutes = []
            if window_start_time_phase_1 and window_end_time_phase_1 and window_start_time_phase_1 == window_start_time_phase_2 and window_end_time_phase_1 == window_end_time_phase_2:
                time_intervals = [[window_start_time_phase_1, window_end_time_phase_1]]
                available_minutes = [((window_end_time_phase_1 - window_start_time_phase_1).total_seconds()) / 60]
            else:
                if window_start_time_phase_1 and window_end_time_phase_1:
                    time_intervals.append([window_start_time_phase_1, window_end_time_phase_1])
                    available_minutes.append((window_end_time_phase_1 - window_start_time_phase_1).total_seconds() / 60)
                if window_start_time_phase_2 and window_end_time_phase_2:
                    time_intervals.append([window_start_time_phase_2, window_end_time_phase_2])
                    available_minutes.append((window_end_time_phase_2 - window_start_time_phase_2).total_seconds() / 60)

            # If There Is One or More Status Entries For A Valid Restaurant Working Hour Slot
            if time_intervals:
                self.compute_restaurant_status_in_intervals(time_intervals, available_minutes, restaurant_status_checks,
                                                            mode='minute', computation='hour')

    def compute_daily_stats(self, reference_timestamp, restaurant_status_checks):
        restaurant_timezone = RestaurantTimezoneInfo.objects.filter(store_id=self.store_id).last()
        if not restaurant_timezone:
            restaurant_timezone = 'America/Chicago'
        else:
            restaurant_timezone = restaurant_timezone.timezone_str

        # Convert TimeSlots Into Local TimzeZone
        query_time_window_end = reference_timestamp.astimezone(pytz.timezone(restaurant_timezone))
        query_time_window_start = query_time_window_end - timedelta(days=1)
        day_of_week_end = query_time_window_end.weekday()
        day_of_week_start = query_time_window_start.weekday()

        # There Will Be Cases Where Our Requested Relative Period lies between 2 dates
        restaurant_operational_hours_start = RestaurantOperationTimeSlots.objects.filter(store_id=self.store_id,
                                                                                         day_of_week=day_of_week_start).last()
        restaurant_operational_hours_end = RestaurantOperationTimeSlots.objects.filter(store_id=self.store_id,
                                                                                       day_of_week=day_of_week_end).last()

        # Abort Further Operations If Restaurant Does Not Operate On A Particular Weekday

        operational_hours_start_phase_1 = datetime.combine(query_time_window_start.date(),
                                                           restaurant_operational_hours_start.start_time_local).replace(
            tzinfo=pytz.UTC) if restaurant_operational_hours_start else None

        operational_hours_end_phase_1 = datetime.combine(query_time_window_start.date(),
                                                         restaurant_operational_hours_start.end_time_local).replace(
            tzinfo=pytz.UTC) if restaurant_operational_hours_start else None
        operational_hours_start_phase_2 = datetime.combine(query_time_window_end.date(),
                                                           restaurant_operational_hours_end.start_time_local).replace(
            tzinfo=pytz.UTC) if restaurant_operational_hours_end else None
        operational_hours_end_phase_2 = datetime.combine(query_time_window_end.date(),
                                                         restaurant_operational_hours_end.end_time_local).replace(
            tzinfo=pytz.UTC) if restaurant_operational_hours_end else None

        if operational_hours_start_phase_1:
            window_start_time_phase_1 = operational_hours_start_phase_1 if operational_hours_start_phase_1 > query_time_window_start else query_time_window_start
        else:
            window_start_time_phase_1 = None
        if operational_hours_end_phase_1:
            window_end_time_phase_1 = operational_hours_end_phase_1 if operational_hours_end_phase_1 < query_time_window_end else query_time_window_end
        else:
            window_end_time_phase_1 = None
        if operational_hours_start_phase_2:
            window_start_time_phase_2 = operational_hours_start_phase_2 if operational_hours_start_phase_2 > query_time_window_start else query_time_window_start
        else:
            window_start_time_phase_2 = None
        if operational_hours_end_phase_2:
            window_end_time_phase_2 = operational_hours_end_phase_2 if operational_hours_end_phase_2 < query_time_window_end else query_time_window_end
        else:
            window_end_time_phase_2 = None

        time_intervals = []
        available_hours = []
        # Designate Time Intervals According To QueryTime, RestaurantSchedules, Store
        if window_start_time_phase_1 and window_end_time_phase_1:
            time_intervals.append([window_start_time_phase_1, window_end_time_phase_1])
            available_hours.append((window_end_time_phase_1 - window_start_time_phase_1).total_seconds() / 3600)
        if window_start_time_phase_2 and window_end_time_phase_2:
            time_intervals.append([window_start_time_phase_2, window_end_time_phase_2])
            available_hours.append((window_end_time_phase_2 - window_start_time_phase_2).total_seconds() / 3600)

        # If There Is One or More Status Entries For A Valid Restaurant Working Hour Slot
        if time_intervals:
            self.compute_restaurant_status_in_intervals(time_intervals, available_hours, restaurant_status_checks,
                                                        mode='hour', computation='day')

    def compute_weekly_stats(self, reference_timestamp, restaurant_status_checks):
        restaurant_timezone = RestaurantTimezoneInfo.objects.filter(store_id=self.store_id).last()
        if not restaurant_timezone:
            restaurant_timezone = 'America/Chicago'
        else:
            restaurant_timezone = restaurant_timezone.timezone_str

        # Convert TimeSlots Into Local TimzeZone
        query_time_window_end = reference_timestamp.astimezone(pytz.timezone(restaurant_timezone))
        query_time_window_start = query_time_window_end - timedelta(days=7)
        day_of_week_start = query_time_window_start.weekday()
        ref_day_of_week = 0  # Counter Which Runs From xth Day Of This Week To x-1th Day Of Next Week
        time_intervals = []
        available_hours = []
        while ref_day_of_week < 7:
            operation_time_slot = RestaurantOperationTimeSlots.objects.filter(store_id=self.store_id,
                                                                              day_of_week=(
                                                                                                  day_of_week_start + ref_day_of_week) % 7).last()
            operational_window_start_time = datetime.combine(
                (query_time_window_start + timedelta(days=ref_day_of_week)).date(),
                operation_time_slot.start_time).replace(tzinfo=pytz.UTC) if operation_time_slot else None
            operational_window_end_time = datetime.combine(query_time_window_end.date(),
                                                           operation_time_slot.end_time_local).replace(
                tzinfo=pytz.UTC) if operation_time_slot else None

            # Abort Further Operations If Restaurant Does Not Operate On A Particular Weekday
            if operational_window_start_time:
                time_interval_start = operational_window_start_time if operational_window_start_time > query_time_window_start else query_time_window_start
            else:
                time_interval_start = None
            if operational_window_end_time:
                time_interval_end = operational_window_end_time if operational_window_end_time < query_time_window_end else query_time_window_end
            else:
                time_interval_end = None
            if time_interval_start and time_interval_end:
                time_intervals.append([time_interval_start, time_interval_end])
                available_hours.append((time_interval_end - time_interval_start).total_seconds() / 3600)
            ref_day_of_week += 1

        # If There Is One or More Status Entries For A Valid Restaurant Working Hour Slot
        if time_intervals:
            self.compute_restaurant_status_in_intervals(time_intervals, available_hours, restaurant_status_checks,
                                                        mode='hour', computation='week')

    def get_report_by_store(self, consolidated_report_id: int, reference_timestamp: Optional[datetime]) -> Optional[Dict]:
        if not reference_timestamp or not isinstance(reference_timestamp, datetime):
            latest_status_record = RestaurantStatusData.objects.filter(store_id=self.store_id).last()
            reference_timestamp = latest_status_record.timestamp_utc
        restaurant_status_checks = RestaurantStatusData.get_store_status_with_reference(self.store_id,
                                                                                        reference_timestamp)
        # print(f"Computing Hourly Stats For {self.store_id}.....")
        self.compute_hourly_stats(reference_timestamp, restaurant_status_checks)
        # print(f"Computing Daily Stats For {self.store_id}.....")
        self.compute_daily_stats(reference_timestamp, restaurant_status_checks)
        # print(f"Computing Weekly Stats For {self.store_id}.....")
        self.compute_weekly_stats(reference_timestamp, restaurant_status_checks)
        data = {
            "store_id": self.store_id,
            "uptime_last_hour": self.uptime_last_hour,
            "uptime_last_day": self.uptime_last_day,
            "uptime_last_week": self.uptime_last_week,
            "downtime_last_hour": self.downtime_last_hour,
            "downtime_last_day": self.downtime_last_day,
            "downtime_last_week": self.downtime_last_week,
            "reference_timestamp": reference_timestamp.strftime(
                "%Y%m%dT%H:%M:%S")
        }
        # print(f"Finished Computing Stats For {self.store_id}")
        normalized_data = json.loads(json.dumps(data, cls=DjangoJSONEncoder))
        restaurant_report = RestaurantReports.objects.create(store_id=self.store_id,
                                                             status=ReportStatus.COMPLETED,
                                                             reference_timestamp=reference_timestamp,
                                                             consolidated_report_id=consolidated_report_id,
                                                             data=normalized_data)
        return restaurant_report
