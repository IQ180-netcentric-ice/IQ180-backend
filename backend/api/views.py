# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from base.models import User, Detail
# from .serializers import UserSerializer, DetailSerializer
# from asgiref.sync import sync_to_async
# from adrf.decorators import api_view
# from django.db import transaction


# @api_view(['GET'])
# def getData(request):
#     person = User.objects.all()
#     serializer = UserSerializer(person, many=True)
#     return Response(serializer.data)


# @api_view(['POST'])
# def postData(request):
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#     return Response(serializer.data)

