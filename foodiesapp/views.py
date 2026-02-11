from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, FoodItem, Profile
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# Create your views here.

def index(request):
    categories = Category.objects.all()

    context = {
        'categories': categories
    }
    return render(request, 'index.html', context)

def food_item(request, pk):
    category = None
    food_items = FoodItem.objects.none()

    if pk:
        category = get_object_or_404(Category, pk=pk)
        food_items = FoodItem.objects.filter(category=category)

    context = {
        'food_items': food_items,
        'category': category,
    }
    return render(request, 'food_item.html', context)


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            user = authenticate(username=form, password=form.cleaned_data['password'])
            if user:
                login(request, user)
                messages.success(request, "You have successfully signed up.")
            return redirect('index')
    else:
        messages.error(request, "Signup failed. Please correct the errors below.")
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('index')

def profile_detail(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'profile_detail.html', {'profile': profile})

def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')
    else:
        
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'profile_update.html', context)


def _get_cart(session):
    return session.setdefault('cart', {})

def add_to_cart(request, food_item_id):
    cart = _get_cart(request.session)
    item = get_object_or_404(FoodItem, id=food_item_id)
    cart[str(item.id)] = cart.get(str(item.id), 0) + 1
    request.session.modified = True
    messages.success(request, f"Added {item.name} to cart.")
    return redirect('food_item', pk=item.category.pk)

def remove_cart(request, food_item_id):
    cart = _get_cart(request.session)
    item_id_str = str(food_item_id)
    if item_id_str in cart:
        del cart[item_id_str]
        request.session.modified = True
        messages.success(request, "Item removed from cart.")
    return redirect('cart_view')

def cart_view(request):
    cart = _get_cart(request.session)
    food_items = []
    total_price = 0

    for item_id, quantity in cart.items():
        item = get_object_or_404(FoodItem, id=item_id)
        item.total_price = item.price * quantity
        item.quantity = quantity
        food_items.append(item)
        total_price += item.total_price

    context = {
        'food_items': food_items,
        'total_price': total_price
    }
    return render(request, 'cart.html', context) 


def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')
    return redirect('create_order')


    # Clear the cart after checkout
    # request.session['cart'] = {}
    # request.session.modified = True
    # messages.success(request, "Checkout successful! Thank you for your order.")
    # return redirect('index')


def create_food_item(request):
    if request.method == 'POST':
        form = CreateFoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            category_name = form.cleaned_data['category']
            category, created = Category.objects.get_or_create(name=category_name)
            FoodItem.objects.create(
                category=category,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                price=form.cleaned_data['price'],
                image=form.cleaned_data['image']
            )
            messages.success(request, "Food item created successfully.")
            return redirect('index')
    else:
        form = CreateFoodItemForm()
    return render(request, 'create_food_item.html', {'form': form})