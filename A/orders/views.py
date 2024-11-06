from django.shortcuts import render,redirect
from django.views import View
from . cart import Cart
from django.shortcuts import get_object_or_404
from home.models import Product
from . forms import CartAddForm, CoupanApplyForm
from django.contrib.auth.mixins import LoginRequiredMixin
from . models import Order, OrderItem, Coupan
import requests
import json
from django.http import HttpResponse
import datetime
from django.contrib import messages
# Create your views here.



class CartView(View):
    def get(self, request):
        cart = Cart(request)
        return render(request, 'orders/cart.html', {'cart': cart})
    
class CartAddView(View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id = product_id)
        form = CartAddForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product, cd['quantity'])
        return redirect('orders:cart')

class CartRemoveView(View):
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id = product_id)
        cart.remove(product)
        return redirect('orders:cart')
    

class OrderDetailView(LoginRequiredMixin, View):
    form_class = CoupanApplyForm

    def get(self, request, order_id):
        order = get_object_or_404(Order, id = order_id)
        return render(request, 'orders/order_detail.html', {'order': order, 'form': self.form_class})

class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user = request.user)
        for item in cart:
            OrderItem.objects.create(order = order, product = item['product'], price = item['price'], quantity = item['quantity'])
        cart.clear()
        return redirect('orders:order_detail', order.id)


ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"

CallbackURL = 'http://127.0.0.1:8080/orders/verify/'
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required

class OrderPayView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = Order.objects.get(id = order_id)
        request.session['order_pay'] = {
            'order_id': order.id,
        }
        req_data = {
        "MerchantID": "00000000-0000-0000-0000-000000000000",
        "Amount": order.get_total_price(),
        "Description": description,
        "CallbackURL": CallbackURL,
        "metadata" : {
            "mobile": request.user.phone_number,
            "email": request.user.email,
            }
        }
        req_header = {
            "accept": "application/json",
            "content-type": "application/json",
        }
        req = requests.post(url=ZP_API_REQUEST, data = json.dumps(
            req_data), headers=req_header)
        authority = req.json()['data']['authority']
        if len(req.json()['errors']) == 0:
            return redirect(ZP_API_STARTPAY.format(authority=authority))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
        
        
class OrderVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        order_id = request.session['order_pay']['order_id']
        order = Order.objects.get(id = int(order_id))
        t_status = request.GET.get('Status')
        t_authority = request.GET['Authority']
        if request.GET.get('status') == 'OK':
            req_header = {"accept": "application/json",
                          "content-type": "application/json"}
            req_data = {
                "merchant_id":  "MerchantID",
                "amount": order.get_total_price(),
                "authority": t_authority
            }
            req = request.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers = req_header)
            if len(req.json()['errors']) == 0:
                t_status = req.json()['data']['code']
                if t_status == 100:
                    order.paid = True
                    order.save()
                    return HttpResponse('Transaction success.\nRefID: ' + str(
                        req.json()['data']['ref_id']
                    ))
                elif t_status == 101:
                    return HttpResponse('Transaction submitted : ' + str(
                        req.json()['data']['messsage']
                    ))
                else:
                    return HttpResponse("Transaction fialed.\nStatus: " + str(
                        req.json()['data']['message']
                    ))

            else:
                e_code = req.json()['errors']['code']
                e_message = req.json()['errors']['message']
                return HttpResponse(f"Error code: {e_code}, Error message: {e_message}")
        else:
            return HttpResponse('Transaction filed or cancelde by user')
        

class CoupanaApplyView(LoginRequiredMixin, View):
    form_class = CoupanApplyForm
    def post(self, request, order_id):
        now = datetime.datetime.now()
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupan = Coupan.objects.get(code__exact = code, valid_from__lte = now, valid_to__gte = now, active = True)
            except Coupan.DoesNotExist:
                messages.error(request, 'this coupan does not exist', 'danger')
                return redirect('orders:order_detail', order_id)
            order = Order.objects.get(id = order_id)
            order.discount = coupan.discount
            order.save()
            return redirect('orders:order_detail', order_id)

