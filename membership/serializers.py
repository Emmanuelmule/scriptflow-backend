from rest_framework import serializers
from .models import Membership

class MembershipSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(source='writer.full_name', read_only=True)

    class Meta:
        model  = Membership
        fields = [
            'id', 'writer', 'writer_name', 'tier', 'amount_kes',
            'mpesa_code', 'phone', 'paid_at', 'expires_at', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'writer', 'mpesa_code', 'paid_at', 'expires_at', 'created_at']


class STKPushSerializer(serializers.Serializer):
    tier  = serializers.ChoiceField(choices=['basic', 'standard', 'premium'])
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        if not value.startswith('07') or len(value) != 10:
            raise serializers.ValidationError("Enter a valid Safaricom number e.g. 0712345678")
        return value