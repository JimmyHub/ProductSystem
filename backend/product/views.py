import json

from django.http import JsonResponse
from rest_framework.generics import GenericAPIView
from django.db import transaction
from django.db.models import Sum

from .models import ProductProfile, ProductManager, ProductReceipt
from .serializers import ProductSerializer, PmanagerSerializer, PreceiptSerializer

key = 'a123456'

DB_DICT = {
    'out_database': 'default',
    'in_database': 'in_account',
}


def take_data(request):
    json_str = request.body
    if json_str:
        json_obj = json.loads(json_str)
        return json_obj


def check_data(data_dict, json_data):
    for data in data_dict:
        item = json_data.get(data, '')
        if not item:
            result = {'code': 400, 'data': {'error': f'請給我商品的 {data}資料'}}
            return False, result
        data_dict[data] = item
    return True, data_dict


class ProductView(GenericAPIView):
    # queryset = ProductProfile.objects.all()
    serializer_class = ProductSerializer

    # 獲取 特定page 的資料
    def select_page_data(self, page, query_list):
        p_max = page * 300
        p_min = (page - 1) * 300
        data_len = len(query_list)
        if data_len < 300:
            min_data_num, max_data_num = 0, data_len

        elif p_max > data_len:
            if data_len > p_min:
                min_data_num, max_data_num = p_min, data_len
        else:
            min_data_num, max_data_num = p_min, p_max
        pcount = data_len // 300 + 1
        pcounts = [i for i in range(1, pcount + 1)]
        query_list = query_list[min_data_num: max_data_num]
        return pcounts, query_list

    # 獲得資料: 獲取全部商品歷史清單 (每一條都要有的那種)
    def get(self, request, pattern, browser, page=1, mode=None, keyword=None, account=None):
        database = DB_DICT.get(account, '')
        if not database:
            result = {'code': 400, 'data': {'error': '選擇錯誤資料庫'}}
            return JsonResponse(result)
        if pattern == 'all':
            product_list = ProductProfile.objects.using(database).all()
        elif pattern == 'all_money':
            in_total = ProductManager.objects.using(database).all().aggregate(Sum('in_price'))
            out_total = ProductManager.objects.using(database).all().aggregate(Sum('out_price'))
            in_total['in_price__sum'] = in_total['in_price__sum'] if in_total['in_price__sum'] else 0
            out_total['out_price__sum'] = out_total['out_price__sum'] if out_total['out_price__sum'] else 0
            result = {'code': 200,
                      'data': {'in_total': in_total['in_price__sum'], 'out_total': out_total['out_price__sum']}}
            return JsonResponse(result)
        elif pattern == 'search':
            # page 資料數量 要小心出錯
            if mode == 'type_no':
                product_list = ProductProfile.objects.using(database).filter(type_no__contains=keyword)
            else:
                product_list = ProductProfile.objects.using(database).filter(kind__contains=keyword)
            if not product_list:
                result = {'code': 400, 'data': {'error': '此關鍵字無效，請重新輸入'}}
                return JsonResponse(result)
        else:
            result = {'code': 400, 'data': {'error': '錯誤瀏覽模式'}}
            return JsonResponse(result)

        result_list = []
        pcounts = 0
        if browser == 'summary':
            pcounts, page_p_list = self.select_page_data(page, product_list)
            for product in page_p_list:
                product_data = {
                    'pid': product.id,
                    'type_no': product.type_no,
                    'kind': product.kind,
                    'total': product.total,
                    'store': product.store
                }
                result_list.append(product_data)
        elif browser == 'history':
            manager_list = ProductManager.objects.using(database).all().order_by('-in_time')
            if manager_list:
                for p in product_list:
                    list_tmp = manager_list.filter(pid=p.id)
                    for manager in list_tmp:
                        out_price = 0 if not manager.out_price else manager.out_price
                        out_time = '' if not manager.out_time else manager.out_time
                        manager_data = {
                            'type_no': manager.pid.type_no,
                            'kind': manager.pid.kind,
                            'store': manager.pid.store,
                            'mid': manager.id,
                            'number': manager.number,
                            'in_price': manager.in_price,
                            'in_time': manager.in_time,
                            'out_price': out_price,
                            'out_time': out_time}
                        result_list.append(manager_data)
                pcounts, result_list = self.select_page_data(page, result_list)
        result = {'code': 200, 'data': {'list': result_list, 'pcounts': pcounts}}
        return JsonResponse(result)

    # 新增商品資料: 新增商品紀錄(數量每一個都會寫入一筆資料到表裡面 同時也在總表加上新數量)
    def post(self, request, account):
        database = DB_DICT.get(account, '')
        if not database:
            result = {'code': 400, 'data': {'error': '選擇錯誤資料庫'}}
            return JsonResponse(result)

        # 先用初版寫法 其他日後再做修改
        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)
        product_dict = {'type_no': '', 'kind': '', 'total': 0, 'in_price': 0, 'in_time': ''}
        # 檢查傳入資料是否有問題
        data_ok = check_data(product_dict, json_obj)
        if not data_ok[0]:
            return JsonResponse(data_ok[1])
        product_dict = data_ok[1]
        with transaction.atomic():
            try:
                # 先看有沒有舊資料
                # product = ProductProfile.objects.get_or_create(**product_dict[1])
                product = ProductProfile.objects.using(database).filter(type_no=product_dict['type_no'])

                if not product:
                    # 根據傳入資料 先把 機型 寫入資料庫
                    product_dict['store'] = product_dict['total']
                    product = ProductProfile.objects.using(database).create(
                                                                            type_no=product_dict['type_no'],
                                                                            kind=product_dict['kind'],
                                                                            total=product_dict['total'],
                                                                            store=product_dict['store'],
                                                                            )
                else:
                    product = product[0]
                    total_num = product.total + int(product_dict['total'])
                    store_num = product.store + int(product_dict['total'])
                    product.total = total_num
                    product.store = store_num
                    product.save(using=database)
                for num in range(int(product_dict['total'])):
                    ProductManager.objects.using(database).create(pid=product,
                                                                            in_price=product_dict['in_price'],
                                                                            in_time=product_dict['in_time'],
                                                                            number=1)
                result = {'code': 200, 'data': {'message': f'{product_dict["type_no"]}新增完成'}}
            except Exception as e:
                result = {'code': 500, 'data': {'error': f'新增資料出現異常:{e}'}}
        return JsonResponse(result)

    # 修改商品資料: 修改 品牌/類型/類別/庫存/總數
    def put(self, request, account=None):
        database = DB_DICT.get(account, '')

        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)
        product_dict = {'id': 0, 'type_no': '', 'kind': '', 'total': 0, 'store': '', }
        data_ok = check_data(product_dict, json_obj)
        if not data_ok[0]:
            return JsonResponse(data_ok[1])
        product_dict = data_ok[1]
        with transaction.atomic():
            try:
                products = ProductProfile.objects.using(database).filter(id=product_dict['id'])
                if not products:
                    result = {'code': 200, 'data': {'error': '請給予商品'}}
                    return JsonResponse(result)
                product = products[0]
                product.type_no = product_dict['type_no']
                product.kind = product_dict['kind']
                product.total = product_dict['total']
                product.store = product_dict['store']
                product.save(using=database)
                result = {'code': 200, 'data': {'message': f'{product_dict["type_no"]}修改完成'}}
            except Exception as e:
                result = {'code': 500, 'data': {'error': '新增資料出現異常'}}
        return JsonResponse(result)


class ProductManagerView(GenericAPIView):
    # queryset = ProductManager.objects.all()
    serializer_class = PmanagerSerializer

    def store_change(self, objects, database, method):
        pid = objects.pid
        pid.store -= 1
        if method == 'delete':
            pid.total -= 1
        pid.save(using=database)

    # 商品銷貨: 新增銷貨時間 跟 銷貨金額 修改商品數量 0 > 1
    def post(self, request, account):
        database = DB_DICT.get(account, '')
        if not database:
            result = {'code': 400, 'data': {'error': '選擇錯誤資料庫'}}
            return JsonResponse(result)

        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)
        product_dict = {'mid': '', 'out_time': '', 'out_price': ''}
        # 檢查傳入資料是否有問題
        data_ok = check_data(product_dict, json_obj)
        if not data_ok[0]:
            return JsonResponse(data_ok[1])
        product_dict = data_ok[1]
        managers = ProductManager.objects.using(database).filter(id=product_dict['mid'])
        if not managers:
            result = {'code': 400, 'data': {'error': '請傳入正確的mid'}}
            return JsonResponse(result)
        manager = managers[0]
        with transaction.atomic():
            try:
                self.store_change(manager, database, 'post')
                manager.number = 0
                manager.out_price = product_dict['out_price']
                manager.out_time = product_dict['out_time']
                manager.save(using=database)
                result = {'code': 200, 'data': {'message': f'{managers[0].pid.type_no}銷貨完成'}}
            except Exception as e:
                result = {'code': 500, 'data': {'error': '商品銷貨 出現異常'}}
        return JsonResponse(result)

    # 修改商品資料: 可修改 品牌/類型/類別/進貨價格/進貨時間/銷貨價格/銷貨時間
    def put(self, request, mid, account):
        database = DB_DICT.get(account, '')
        if not database:
            result = {'code': 400, 'data': {'error': '選擇錯誤資料庫'}}
            return JsonResponse(result)

        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)
        product_dict = {'mid': 0, 'type_no': '', 'kind': '', 'in_price': 0, 'in_time': '', }
        data_ok = check_data(product_dict, json_obj)
        if not data_ok[0]:
            return JsonResponse(data_ok[1])
        product_dict = data_ok[1]
        product_dict['out_price'] = json_obj.get('out_price')
        product_dict['out_time'] = json_obj.get('out_time')
        with transaction.atomic():
            try:
                manages = ProductManager.objects.using(database).filter(id=mid)
                if not manages:
                    result = {'code': 200, 'data': {'error': '請給予商品'}}
                    return JsonResponse(result)
                manage = manages[0]
                manage.in_price = product_dict['in_price']
                manage.in_time = product_dict['in_time']
                manage.out_price = product_dict['out_price']
                if product_dict['out_time']:
                    manage.out_time = product_dict['out_time']

                product = manage.pid
                product.kind = product_dict['kind']
                product.type_no = product_dict['type_no']
                manage.save(using=database)
                product.save(using=database)
                result = {'code': 200, 'data': {'message': f'{product_dict["type_no"]}修改完成'}}
            except Exception as e:
                result = {'code': 500, 'data': {'error': f'新增資料出現異常: {e}'}}
        return JsonResponse(result)

    # 商品刪除: 刪除商品個別紀錄(包含 個別資料刪除/總表資料數量-1)
    def delete(self, request, mid, account):
        # 先用初版寫法 其他日後再做修改
        database = DB_DICT.get(account, '')
        if not database:
            result = {'code': 400, 'data': {'error': '選擇錯誤資料庫'}}
            return JsonResponse(result)

        manager = ProductManager.objects.using(database).filter(id=mid)
        if not manager:
            result = {'code': 400, 'data': {'error': f'商品{id} 傳送錯誤'}}
            return JsonResponse(result)
        manager = manager[0]
        with transaction.atomic():
            try:
                self.store_change(manager, database, 'delete')
                type_no = manager.pid.type_no
                manager.delete(using=database)
                result = {'code': 200, 'data': {'message': f'{type_no} 刪除完成'}}
            except Exception as e:
                result = {'code': 500, 'data': {'error': '刪除資料出現異常'}}
        return JsonResponse(result)


class ProductReceiptView(GenericAPIView):
    # queryset = ProductReceipt.objects.all()
    serializer_class = PreceiptSerializer

    # 發票開立: 修改發票狀態
    def put(self, request):

        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)

        receipt = ProductReceipt.objects.filter(mid_id=json_obj['mid'])
        if not receipt:
            result = {'code': 400, 'data': {'error': '此發票紀錄不存在'}}
            return JsonResponse(result)
        with transaction.atomic():
            try:
                receipt[0].status = 1
                receipt[0].save(using=database)
                result = {'code': 200, 'data': {'message': '發票開立紀錄完成'}}

            except Exception as e:
                result = {'code': 500, 'data': {'error': '發票狀態修改出現異常'}}
        return JsonResponse(result)

    # 發票刪除: 發票錯誤 需要重新設定
    def delete(self, request):
        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)
        receipt = ProductReceipt.objects.filter(mid_id=json_obj['mid'])
        if not receipt:
            result = {'code': 400, 'data': {'error': '發票資料錯誤'}}
            return JsonResponse(result)
        manager = receipt[0].mid
        with transaction.atomic():
            try:
                receipt[0].delete()
                ProductReceipt.objects.create(mid=manager)
                result = {'code': 200, 'data': {'message': '發票紀錄重置完成'}}
            except Exception as e:
                result = {'code': 500, 'data': {'error': '發票狀態修改出現異常'}}
        return JsonResponse(result)
