import json

from django.http import JsonResponse
from rest_framework.generics import GenericAPIView
from django.db import transaction

from .models import ProductProfile, ProductManager, ProductReceipt
from .serializers import ProductSerializer, PmanagerSerializer, PreceiptSerializer

key = 'a123456'


def take_data(request):
    json_str = request.body
    if json_str:
        json_obj = json.loads(json_str)
        return json_obj


class ProductView(GenericAPIView):
    # queryset = ProductProfile.objects.all()
    serializer_class = ProductSerializer

    def check_data(self, data_dict, json_data):
        for data in data_dict:
            item = json_data.get(data, '')
            if not item:
                result = {'code': 400, 'data': {'error': f'請給我商品的 {data}資料'}}
                return False, result
            data_dict[data] = item

    # 獲得資料: 獲取全部商品歷史清單 (每一條都要有的那種)
    def get(self, request, pattern, browser, keyword):
        if pattern == 'all':
            product_list = ProductProfile.object.all()
        elif pattern == 'kind':
            product_list = ProductProfile.object.filter(kind=keyword)
        else:
            result = {'code': 400, 'data': {'error': '錯誤瀏覽模式'}}
            return JsonResponse(result)

        result_list = []
        if browser == 'summary':
            for product in product_list:
                p_file = product.pid
                product_data = {
                    'brand': p_file.brand,
                    'type_no': p_file.type_no,
                    'kind': p_file.kind,
                    'total': product.total
                }
                result_list.append(product_data)
        elif browser == 'history':
            for product in product_list:
                manager_list = ProductManager.object.filter(pid=product)
                manager_tmp_list = []
                if not manager_list:
                    result = {'code': 400, 'data': {'error': 'manager 資料庫有誤'}}
                    return JsonResponse(result)
                for manager in manager_list:
                    receipt = ProductReceipt.object.filter(mid=manager)
                    manager_data = {'number': manager.number, 'in_time': manager.in_time,
                                    'out_time': manager.out_time, 'price': manager.price,
                                    'receipt': receipt[0].make_time}
                    manager_tmp_list.append(manager_data)
                product_data = {'brand': product.brand, 'type_no': product.type_no,
                                'kind': product.kind, 'p_list': manager_tmp_list
                                }
                result_list.append(product_data)
        result = {'code': 200, 'data': result_list}
        return JsonResponse(result)

    # 新增商品資料: 新增商品紀錄(數量每一個都會寫入一筆資料到表裡面 同時也在總表加上新數量)
    def post(self, request):
        # 先用初版寫法 其他日後再做修改
        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)
        product_dict = {'brand': '', 'type_no': '', 'kind': '', 'total': 0}
        # 檢查傳入資料是否有問題
        data_ok = self.check_data(product_dict, json_obj)
        if not data_ok[0]:
            return JsonResponse(data_ok[1])
        with transaction.atomic():
            try:
                # 先看有沒有舊資料
                # product = ProductProfile.object.get_or_create(**product_dict[1])
                product = ProductProfile.object.filter(type_no=product_dict['type_no'])
                if not product:
                    # 根據傳入資料 先把 機型 寫入資料庫
                    product = ProductProfile.object.create(**product_dict)
                else:
                    product = product[0]
                    product.update(total=product.total + product_dict['total'])
                    product.save()
                for num in range(product_dict['total']):
                    manager = ProductManager.object.create(pid=product,
                                                           number=1)
                    ProductReceipt.object.create(mid=manager, status=0)
                result = {'code': 200, 'data': f'{product_dict["type_no"]}新增完成'}
            except Exception as e:
                result = {'code': 500, 'data': {'error': '新增資料出現異常'}}
        return JsonResponse(result)

    # 修改商品資料: 只能修改 品牌/類型/類別
    def put(self, request):
        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)
        product_dict = {'id': 0, 'brand': '', 'type_no': '', 'kind': '', 'total': 0}
        data_ok = self.check_data(product_dict, json_obj)
        if not data_ok[0]:
            return JsonResponse(data_ok[1])
        with transaction.atomic():
            try:
                product = ProductProfile.object.filter(id=product_dict['id'])
                if not product:
                    result = {'code': 200, 'data': {'error': '請給予商品'}}
                    return JsonResponse(result)
                product[0].update(**product_dict)
                product[0].save()
                result = {'code': 200, 'data': f'{product_dict["type_no"]}新增完成'}
            except Exception as e:
                result = {'code': 500, 'data': {'error': '新增資料出現異常'}}
        return JsonResponse(result)


class ProductManagerView(GenericAPIView):
    # queryset = ProductManager.objects.all()
    serializer_class = PmanagerSerializer


    def total_change(self,object):
        pid = object.pid
        pid.update(total=pid.total - 1)
        pid.save()

    # 商品銷貨: 修改商品數量 0 > 1
    def put(self, request):
        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)
        mid = json_obj.get('mid', '')
        managers = ProductManager.object.filter(id=mid)
        if not managers:
            result = {'code': 400, 'data': {'error': '請傳入正確的mid'}}
            return JsonResponse(result)
        manager = managers[0]
        with transaction.atomic():
            try:
                self.total_change(manager)
                manager.update(number=0)
                manager.save()
                result = {'code': 200, 'data': f'{managers[0].pid.type_no}銷貨完成'}
            except Exception as e:
                result = {'code': 500, 'data': {'error': '商品銷貨 出現異常'}}
        return JsonResponse(result)

    # 商品刪除: 刪除商品個別紀錄(包含 個別資料刪除/總表資料數量-1)
    def delete(self, request):
        # 先用初版寫法 其他日後再做修改
        json_obj = take_data(request)
        if not json_obj:
            result = {'code': 400, 'data': {'error': '請傳送資料'}}
            return JsonResponse(result)

        mid = json_obj.get('mid', '')
        if not mid:
            result = {'code': 400, 'data': {'error': '商品id 傳送錯誤'}}
            return JsonResponse(result)

        manager = ProductManager.object.filter(id=mid)
        if not manager:
            result = {'code': 400, 'data': {'error': f'商品id 傳送錯誤'}}
            return JsonResponse(result)

        with transaction.atomic():
            try:
                self.total_change(manager)
                manager[0].delete()
                result = {'code': 200, 'data': {'message': f'{mid}號紀錄，刪除完成'}}
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

        receipt = ProductReceipt.object.filter(mid_id=json_obj['mid'])
        if not receipt:
            result = {'code': 400, 'data': {'error': '此發票紀錄不存在'}}
            return JsonResponse(result)
        with transaction.atomic():
            try:
                receipt[0].status = 1
                receipt[0].save()
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
        receipt = ProductReceipt.object.filter(mid_id=json_obj['mid'])
        if not receipt:
            result = {'code': 400, 'data': {'error': '發票資料錯誤'}}
            return JsonResponse(result)
        manager = receipt[0].mid
        with transaction.atomic():
            try:
                receipt[0].delete()
                ProductReceipt.object.create(mid=manager)
                result = {'code': 200, 'data': {'message': '發票紀錄重置完成'}}
            except Exception as e:
                result = {'code': 500, 'data': {'error': '發票狀態修改出現異常'}}
        return JsonResponse(result)
