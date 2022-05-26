from rest_framework import serializers
from .models import UserProject


class UserProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProject
        fields = ['name', 'user', 'created_date', 'projectId']
