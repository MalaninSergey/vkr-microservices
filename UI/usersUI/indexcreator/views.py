import json
import uuid
import pandas as pd
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from elasticsearch import Elasticsearch

from .models import UserProject
from .serializers import UserProjectSerializer


class UserProjectApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request, *args, **kwargs):
        projects = UserProject.objects.filter(user=request.user.id)
        serializer = UserProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request, *args, **kwargs):
        project_name = request.data['name']
        new_project_id = uuid.uuid4().hex
        data = {
            'name': project_name,
            'user': request.user.id,
            'projectId': new_project_id
        }

        serializer = UserProjectSerializer(data=data)
        if serializer.is_valid():
            project = serializer.save()
            project.create_index(request.data['fields'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def put_data_to_index(request):
    if request.method == 'POST':
        es = Elasticsearch(hosts=["http://elasticsearch:9200/"])
        if len(request.FILES):
            index_name = request.POST['name'] + '_products_' + request.POST['projectId']
            print(request.POST['name'])
            extension = request.FILES['data'].name.split('.')[-1].lower()
            df = pd.DataFrame()
            if extension == 'csv':
                df = pd.read_csv(request.FILES['data'])
            elif extension == 'xlsx':
                df = pd.read_excel(request.FILES['data'])
            elif extension == 'parquet':
                df = pd.read_parquet(request.FILES['data'])
            elif extension == 'pickle':
                df = pd.read_pickle(request.FILES['data'])
            if es.indices.exists(index=index_name):
                for doc in df.apply(lambda x: x.to_dict(), axis=1):
                    es.index(index=index_name, body=json.dumps(doc))
                return JsonResponse({"Info": "Data pushed"}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"Error": "Index not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            data = json.loads(request.body)
            index_name = data['name'] + '_products_' + data['projectId']
            if es.indices.exists(index=index_name):
                es.index(index=index_name, body=data['document'])
                return JsonResponse(['document'], status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"Error": "Index not found"}, status=status.HTTP_404_NOT_FOUND)


def delete_index(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        index_name = data['name'] + '_products_' + data['projectId']
        es = Elasticsearch(hosts=["http://elasticsearch:9200/"])
        es.indices.delete(index=index_name)
        project = UserProject.objects.get(projectId=data['projectId'])
        project.delete()
        return JsonResponse({'Info': "Deleted"}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'Error': 'Wrong http response method'})
