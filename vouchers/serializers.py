from rest_framework import serializers
from .models import VoucherCategory, VoucherFile, Vouchers, VoucherLogs, VoucherUser
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class VoucherCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherCategory
        fields = '__all__'


class VoucherFileSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = VoucherFile
        fields = ['id', 'name', 'file', 'category', 'category_name', 'user', 'user_detail', 'date_created', 'status']
        read_only_fields = ['date_created']


class VouchersSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    file_name = serializers.CharField(source='file.name', read_only=True)
    file_category = serializers.CharField(source='file.category.name', read_only=True)
    
    class Meta:
        model = Vouchers
        fields = ['id', 'voucher_no', 'file', 'file_name', 'file_category', 'user', 'user_detail', 
                  'date_created', 'date_used', 'date_printed', 'status', 'active', 'validity_duration',
                  'expiry_time', 'bandwidth_up', 'bandwidth_down', 'synced_to_pfsense']
        read_only_fields = ['id', 'date_created', 'date_used', 'date_printed']


class VoucherLogsSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = VoucherLogs
        fields = ['id', 'user', 'user_detail', 'action', 'action_type', 'date_created', 'ip_address']
        read_only_fields = ['date_created']


class VoucherUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherUser
        fields = ['id', 'voucher', 'voucher_no', 'name', 'phonenumber', 'email', 'date_created', 
                  'device_mac', 'last_used_ip']
        read_only_fields = ['date_created']


class VoucherFileDetailSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    category_detail = VoucherCategorySerializer(source='category', read_only=True)
    vouchers = serializers.SerializerMethodField()
    
    class Meta:
        model = VoucherFile
        fields = ['id', 'name', 'file', 'category', 'category_detail', 'user', 
                  'user_detail', 'date_created', 'status', 'vouchers']
        read_only_fields = ['date_created']
    
    def get_vouchers(self, obj):
        voucher_objs = Vouchers.objects.filter(file=obj)
        return VouchersSerializer(voucher_objs, many=True).data


class VoucherDetailSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    file_detail = VoucherFileSerializer(source='file', read_only=True)
    voucher_user_detail = VoucherUserSerializer(source='voucher_user', read_only=True)
    
    class Meta:
        model = Vouchers
        fields = ['id', 'voucher_no', 'file', 'file_detail', 'user', 'user_detail', 
                  'date_created', 'date_used', 'date_printed', 'status', 'active', 
                  'validity_duration', 'expiry_time', 'bandwidth_up', 'bandwidth_down',
                  'pfsense_roll_id', 'synced_to_pfsense', 'voucher_user_detail']
        read_only_fields = ['id', 'date_created', 'date_used', 'date_printed']