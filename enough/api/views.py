from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from enough.api.permissions import IsEnoughGroupMember
from enough.common import bind, hosting


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated, IsEnoughGroupMember))
def delegate_test_dns(request):
    return JsonResponse(bind.delegate_dns(
        f'test.{settings.ENOUGH_DOMAIN}',
        request.data['name'],
        request.data['ip'],
    ), safe=False, status=201)


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated, IsEnoughGroupMember))
def create_or_upgrade(request):
    return JsonResponse(hosting.Hosting(request.data['name']).create_or_upgrade(),
                        safe=False, status=201)


@api_view(['DELETE'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated, IsEnoughGroupMember))
def delete(request, name):
    return JsonResponse(hosting.Hosting(name).delete(),
                        status=204)
