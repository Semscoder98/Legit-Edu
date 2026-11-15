from rest_framework import serializers
from .models import Scholarship

class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = '__all__'
        read_only_fields = ['slug']
