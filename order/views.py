from django.shortcuts import render, redirect, get_object_or_404

from .models import Order, OrderItem
from .forms import CheckoutForm
from django.contrib import messages
from foodiesapp.models import FoodItem
from decimal import Decimal
# Create your views here.

def _cart_item(request):
    cart = request.session.get('cart', {})
    for item_id, qty in cart.items():
        try:
            m = FoodItem.objects.get(id=item_id)
            yield m, qty
        except FoodItem.DoesNotExist:
            continue


def create_order(request):
    cart = request.session.get('cart', {})
    # normalize cart -> dict of item_id -> qty
    if not cart:
        messages.error(request, 'Your cart is empty')
        return redirect('index')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # materialize cart items since _cart_item is a generator
            items_list = list(_cart_item(request))
            if not items_list:
                messages.error(request, 'Your cart is empty')
                return redirect('checkout')

            # create a parent Order record that satisfies the current model's required fields
            total_qty = sum(qty for _, qty in items_list)
            first_item = items_list[0][0]

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                food_item=first_item,
                name=form.cleaned_data.get('name', ''),
                quantity=total_qty,
                address=form.cleaned_data.get('address', ''),
                total_amount=Decimal('0.00'),
                phone=form.cleaned_data.get('phone', ''),
               
                status='Pending',
            )

            total = Decimal('0.00')
            for m, qty in items_list:
                # create OrderItem entries for each cart item
                OrderItem.objects.create(order=order, food_item=m, quantity=qty, price=m.price)
                total += (m.price * qty)

            order.total_amount = total
            order.save()

            # clear the session cart
            request.session['cart'] = {}
            request.session['current_order_id'] = order.id
            messages.success(request, 'Order created successfully')
            return redirect('pay')
    else:
        form = CheckoutForm()

    # prepare context for GET: use keys expected by template
    cart_items = []
    items_list = list(_cart_item(request))
    for m, qty in items_list:
        cart_items.append({'food_item': m, 'quantity': qty})

    total = sum((m.price * qty) for m, qty in items_list)
    return render(request, 'checkout.html', {'form': form, 'cart_items': cart_items, 'total': total})

def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_details.html', {'order': order})