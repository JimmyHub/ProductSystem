# Generated by Django 4.0.2 on 2022-10-06 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductManager',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('number', models.IntegerField(verbose_name='數量')),
                ('in_time', models.DateField(verbose_name='進貨時間')),
                ('out_time', models.DateField(verbose_name='銷貨時間')),
                ('inprice', models.IntegerField(default=0, verbose_name='進貨金額')),
            ],
            options={
                'db_table': 'products_inout',
            },
        ),
        migrations.CreateModel(
            name='ProductProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(max_length=10, verbose_name='品牌')),
                ('kind', models.CharField(max_length=20, verbose_name='類別')),
                ('type_no', models.CharField(max_length=50, verbose_name='型號')),
                ('total', models.IntegerField(default=0, verbose_name='商品總數')),
                ('store', models.IntegerField(default=0, verbose_name='商品庫存')),
            ],
            options={
                'db_table': 'products_file',
            },
        ),
        migrations.CreateModel(
            name='ProductReceipt',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.IntegerField(default=0, verbose_name='發票狀態')),
                ('make_time', models.DateField(verbose_name='開發票時間')),
                ('outprice', models.IntegerField(default=0, verbose_name='銷貨金額')),
                ('mid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productmanager')),
            ],
            options={
                'db_table': 'products_receipt',
            },
        ),
        migrations.CreateModel(
            name='ProductUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='待增加', max_length=50, verbose_name='名稱')),
                ('tax_id', models.CharField(default='0', max_length=10, verbose_name='統編')),
                ('kind', models.IntegerField(default=0, verbose_name='公司/個人')),
                ('rid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productreceipt')),
            ],
            options={
                'db_table': 'products_user',
            },
        ),
        migrations.AddField(
            model_name='productmanager',
            name='pid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productprofile'),
        ),
    ]
