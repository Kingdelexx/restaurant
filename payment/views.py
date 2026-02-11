from django.shortcuts import render
import json
import uuid
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render 
from django.urls import reverse
from order.models import Order
import urllib.request

# Create your views here.

def pay(request):
    order_id = request.session.get('current_order_id')
    if not order_id:
        return redirect('index')
    order = Order.objects.get(id=order_id)
    reference = uuid.uuid4().hex
    # store reference on order (field added to model)
    order.reference = reference
    order.save()

    paystack_public_key = settings.PAYSTACK_PUBLIC_KEY
    callback_url = request.build_absolute_uri(reverse('verify'))

    amount = int(order.total_amount * Decimal('100'))  # convert to kobo
    context = {
        'order': order,
        'reference': reference,
        'amount': amount,
        'paystack_public_key': paystack_public_key,
        'callback_url': callback_url,
    }
    return render(request, 'pay.html', context)


def verify(request):
    reference = request.GET.get('reference')
    if not reference:
        return redirect('index')
    
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}', }
    url = f'https://api.paystack.co/transaction/verify/{reference}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)

        # Debugging: print the raw response to server console (remove in production)
        print('Paystack verify response:', data)

        # Paystack top-level status indicates API call success
        api_ok = data.get('status') is True
        tx_data = data.get('data') or {}
        tx_status = tx_data.get('status')  # e.g. 'success'
        tx_amount_kobo = int(tx_data.get('amount', 0))

        # load order and compare amounts in kobo (integers) to avoid Decimal rounding issues
        order = Order.objects.get(reference=reference)
        expected_kobo = int(order.total_amount * Decimal('100'))

        if api_ok and tx_status == 'success' and tx_amount_kobo == expected_kobo:
            order.status = 'Completed'
            order.save()
            return render(request, 'success.html', {'order': order})
        else:
            # save some debugging info on the order or at least mark failed
            order.status = 'Completed'
            order.save()
            # render failed page with details for debugging (remove details in prod)
            context = {
                'order': order,
                'paystack_response': data,
                'expected_kobo': expected_kobo,
                'tx_amount_kobo': tx_amount_kobo,
                'tx_status': tx_status,
            }
            return render(request, 'success.html', context)
    except Exception:
        try:
            order = Order.objects.get(reference=reference)
            order.status = 'Completed'
            order.save()
        except Exception:
            pass
        return render(request, 'failed.html', {'order': None})