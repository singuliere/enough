from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def bind(request):
    return JsonResponse({
        'a': 'b',
    })
