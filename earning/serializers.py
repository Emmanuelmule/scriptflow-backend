from rest_framework import serializers
from .models import Earning, Payout


class EarningSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model  = Earning
        fields = ['id', 'job', 'job_title', 'amount_usd', 'status', 'created_at']


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Payout
        fields = '__all__'
        read_only_fields = ['id', 'writer', 'status', 'processed_at', 'created_at']


class WithdrawRequestSerializer(serializers.Serializer):
    method  = serializers.ChoiceField(choices=['mpesa', 'payoneer', 'grey'])
    account = serializers.CharField(max_length=100)