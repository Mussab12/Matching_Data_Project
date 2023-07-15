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
        if isinstance(obj.data1, list):
            for item in obj.data1:
                if isinstance(item, dict):
                    keys.extend(list(item.keys()))
        return keys

    class Meta:
        model = CustomerMaster
        fields = ['keys']


class CustomerMasterSerializer(serializers.ModelSerializer):
    # relationship = serializers.PrimaryKeyRelatedField(
    #     many=False, read_only=True)
    relationship = RelatedCustomerSerializer(many=False, read_only=True)

    # def get_relationship(self, obj):
    #     if obj.relationship:
    #         related_data = {
    #             'id': obj.relationship.id,
    #             'data1': obj.relationship.data1
    #         }
    #         return related_data
    #     return None

    class Meta:
        model = CustomerMaster
        fields = ['id', 'data1', 'relationship']


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