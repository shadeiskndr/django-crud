from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

@api_view(['GET'])
def hello_world(request):
    return Response({
        'message': 'Hello from Django backend!',
        'status': 'success',
        'python_version': '3.13.5',
        'django_backend': 'running'
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def api_test(request):
    if request.method == 'GET':
        return Response({
            'method': 'GET', 
            'message': 'This is a GET request',
            'endpoints': [
                '/api/hello/',
                '/api/test/',
            ]
        })
    elif request.method == 'POST':
        return Response({
            'method': 'POST', 
            'message': 'Data received successfully',
            'received_data': request.data
        }, status=status.HTTP_201_CREATED)

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'Django Backend',
        'version': '1.0.0'
    })
