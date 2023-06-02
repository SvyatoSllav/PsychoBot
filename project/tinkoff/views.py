from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from Acquirers.Tinkoff import TinkoffSimplePayment


class TinkoffWebhook(APIView):
    def post(self, request):
        try:
            logger.info(request.data)

            return JsonResponse({"success": request.data})
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})
