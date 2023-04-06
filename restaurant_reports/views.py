from rest_framework.views import APIView
from restaurant_reports.services.trigger_report import TriggerReportService
from rest_framework.response import Response


class ReportRenderAPI(APIView):

    def post(self, *args, **kwargs):
        report_trigger = TriggerReportService.create_report_request()
        return Response(report_trigger)


class GetRenderedReportAPI(APIView):

    def get(self, request, *args, **kwargs):
        report_id = request.GET.get('report_id')
        rendered_report = TriggerReportService.get_report_if_completed(report_id=report_id)
        response = Response(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=export.csv'
        rendered_report.to_csv(response)
        return response
