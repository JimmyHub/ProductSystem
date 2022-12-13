from django.db import models
import django

class ProductProfile(models.Model):
    id = models.AutoField(primary_key=True)
    kind = models.CharField(verbose_name='類別', max_length=20)
    type_no = models.CharField(verbose_name='型號', max_length=50)
    total = models.IntegerField(verbose_name='商品總數', default=0)
    store = models.IntegerField(verbose_name='商品庫存',default=0)

    class Meta:
        db_table = 'products_file'


class ProductManager(models.Model):
    id = models.AutoField(primary_key=True)
    # 當商品不存在的時候，進出貨資料也會跟著消失
    pid = models.ForeignKey(ProductProfile, on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name='數量')
    in_price = models.IntegerField(verbose_name='進貨金額', default=0)
    in_time = models.DateField(verbose_name='進貨時間')
    out_price = models.IntegerField(verbose_name='銷貨金額', null=True)
    out_time = models.DateField(verbose_name='銷貨時間',null=True)


    class Meta:
        db_table = 'products_inout'


class ProductReceipt(models.Model):
    id = models.AutoField(primary_key=True)
    mid = models.ForeignKey(ProductManager, on_delete=models.CASCADE)
    status = models.IntegerField(verbose_name='發票狀態',default = 0)
    make_time = models.DateField(verbose_name='開發票時間')


    class Meta:
        db_table = 'products_receipt'

class ProductUser(models.Model):
    id = models.AutoField(primary_key=True)
    rid = models.ForeignKey(ProductReceipt, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='名稱',max_length=50, default='待增加')
    tax_id = models.CharField(verbose_name='統編', max_length=10, default='0')
    # 0 個人 1公司
    kind = models.IntegerField(verbose_name='公司/個人', default=0)


    class Meta:
        db_table = 'products_user'