from rest_framework import serializers
from .models import exceldata
from .models import CustomerMaster, NewProsectRecords, MatchingConfig


class ExceldataSerializer(serializers.ModelSerializer):
    class Meta:
        model = exceldata
        fields = ['company_name']


# data1 to data1 relationship
class RelatedCustomerSerializer(serializers.ModelSerializer):
    keys = serializers.SerializerMethodField()

    def get_keys(self, obj):
        keys = []
        if isinstance(obj.data, list):
            for item in obj.data:
                if isinstance(item, dict):
                    keys.extend(list(item.keys()))
        return keys

    def get_keys_data2(self, obj):
        keys = []
        if isinstance(obj.data2, list):
            for item in obj.data2:
                if isinstance(item, dict):
                    keys.extend(list(item.keys()))
        return keys

    class Meta:
        model = CustomerMaster
        fields = ['keys_data1', 'keys_data2']


class CustomerMasterSerializer(serializers.ModelSerializer):
    # relationship = serializers.PrimaryKeyRelatedField(
    #     many=False, read_only=True)
    relationship = RelatedCustomerSerializer(many=False, read_only=True)

    class Meta:
        model = CustomerMaster
        fields = '__all__'

    # def get_relationship(self, obj):
    #     if obj.relationship:
    #         related_data = {
    #             'id': obj.relationship.id,
    #             'data1': obj.relationship.data1
    #         }
    #         return related_data
    #     return None


class MatchingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingConfig
        fields = "__all__"


class NewProspectRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewProsectRecords
        fields = ['CompanyName', 'Industry', 'Address', 'City', 'State', 'ZIP', 'ContactFirstName', 'ContactMiddleInitial',
                  'ContactLastName', 'Phone', 'BirthDate', 'Email', 'AccountCode', 'NationalId', 'CreationDate', 'ModifyDate', 'DemoReference']


class ModelNameSerializer(serializers.Serializer):
    model_name = serializers.SerializerMethodField()

    def get_model_name(self, obj):
        return obj['model_name']
