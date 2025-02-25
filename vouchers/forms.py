from django.forms import ModelForm
from vouchers.models import VoucherFile, Vouchers, VoucherCategory, VoucherUser

class AddVoucherFileForm(ModelForm):
    
    class Meta:
        model = VoucherFile
        fields = ('name', 'file', 'category')


class VoucherForm(ModelForm):
    
    class Meta:
        model = Vouchers
        fields = ('status',)

class CategoryForm(ModelForm):
    
    class Meta:
        model = VoucherCategory
        fields = '__all__'

class VoucherUserForm(ModelForm):
    
    class Meta:
        model = VoucherUser
        exclude = ('voucher_no',)
