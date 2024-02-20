from rest_framework.views import APIView
from restaurant_reports.services.trigger_report import TriggerReportService
from django.http import HttpResponse
import json


class ReportRenderAPI(APIView):

    def post(self, *args, **kwargs):
        report_trigger = TriggerReportService.create_report_request()
        return HttpResponse(json.dumps(report_trigger), content_type='application/json')


class GetRenderedReportAPI(APIView):

    def get(self, request, *args, **kwargs):
        report_id = request.GET.get('report_id')
        rendered_report = TriggerReportService.get_report_if_completed(report_id=report_id)
        if rendered_report:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=export.csv'
            rendered_report.to_csv(response)
            return response
        else:
            return HttpResponse({"data": "Processing In Progress. Please Wait"})