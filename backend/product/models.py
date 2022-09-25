from django.db import models


class ProductProfile(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.CharField(verbose_name='品牌', max_length=10)
    type_no = models.CharField(verbose_name='型號', max_length=50)
    kind = models.CharField(verbose_name='類別', max_length=20)
    total = models.IntegerField(verbose_name='商品總數', default=0)

    class Meta:
        db_table = 'products_file'


class ProductManager(models.Model):
    id = models.AutoField(primary_key=True)
    # 當商品不存在的時候，進出貨資料也會跟著消失
    pid = models.ForeignKey(ProductProfile, on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name='數量')
    in_time = models.DateField(verbose_name='進貨時間', auto_now_add=True)
    out_time = models.DateField(verbose_name='銷貨時間', auto_now=True)
    price = models.IntegerField(verbose_name='銷貨金額', default=0)

    class Meta:
        db_table = 'products_inout'


class ProductReceipt(models.Model):
    mid = models.ForeignKey(ProductManager, on_delete=models.CASCADE, primary_key=True)
    status = models.IntegerField(verbose_name='發票狀態', default=0)
    make_time = models.DateField(verbose_name='開發票時間', auto_now=True)

    class Meta:
        db_table = 'products_receipt'