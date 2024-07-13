from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets
from .models import Product, CarouselItem, Comment, Rating, Order, Cart, CartItem, Subscriber, Announcement
from .serializers import ProductSerializer
from django.db.models import Q
from .forms import CommentForm, UserRegisterForm, UserLoginForm, QueryForm, SubscriberForm, AnnouncementForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
import json
import random
import string
import logging

logger = logging.getLogger(__name__)

def home(request):
    featured_products = Product.objects.filter(featured=True)
    carousel_items = CarouselItem.objects.filter(is_active=True).order_by('created_at')
    subscribed = Subscriber.objects.filter(user=request.user).exists() if request.user.is_authenticated else False
    return render(request, 'index.html', {'featured_products': featured_products, 'carousel_items': carousel_items, 'subscribed': subscribed})

def product_list(request, category=None):
    query = request.GET.get('q')
    sort_by = request.GET.get('sort', 'name')
    products = Product.objects.all()
    if category:
        products = products.filter(category=category)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query)).order_by(sort_by)
    else:
        products = products.order_by(sort_by)
    return render(request, 'product_list.html', {'products': products})

def about_us(request):
    return render(request, 'about_us.html')

def contact_us(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            if request.user.is_authenticated:
                query.user = request.user
                query.name = request.user.username
                query.email = request.user.email
            query.save()
            return redirect('contact_us')
    else:
        form = QueryForm()
    return render(request, 'contact_us.html', {'form': form})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user or request.user.is_superuser:
        comment.delete()
        messages.success(request, 'Comment deleted successfully')
    else:
        messages.error(request, 'You do not have permission to delete this comment')
    return redirect('product_detail', pk=comment.product.pk)

def product_by_category(request, category):
    products = Product.objects.filter(category=category)
    return render(request, 'product_list.html', {'products': products, 'category': category})

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

@csrf_exempt
def rate_product(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        rating_value = data.get('rating')
        product = get_object_or_404(Product, id=product_id)
        user = request.user
        rating, created = Rating.objects.get_or_create(user=user, product=product)
        rating.rating = rating_value
        rating.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def add_rating(request, product_id):
    if request.method == 'POST':
        user = request.user
        product = get_object_or_404(Product, id=product_id)
        data = json.loads(request.body)
        rating_value = data.get('rating')
        if rating_value:
            rating, created = Rating.objects.get_or_create(user=user, product=product, defaults={'rating': rating_value})
            if not created:
                rating.rating = rating_value
                rating.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Invalid rating value'})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    recommended_products = Product.objects.filter(category=product.category).exclude(pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = product
            comment.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = CommentForm()
    return render(request, 'product_detail.html', {'product': product, 'form': form, 'recommended_products': recommended_products})

@csrf_exempt
def send_verification_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({'success': False, 'error': 'Email address is required.'}, status=400)
            verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            try:
                send_mail(
                    'Your Verification Code',
                    f'Your verification code is {verification_code}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
            except BadHeaderError:
                return HttpResponse('Invalid header found.', status=400)
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            logger.error('Failed to decode JSON', exc_info=True)
            return JsonResponse({'success': False, 'error': 'Invalid JSON payload.'}, status=400)
        except Exception as e:
            logger.error('Unexpected error', exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    current_site = get_current_site(request)
                    mail_subject = 'Reset your password'
                    message = render_to_string('password_reset_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                    })
                    send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [email])
                return render(request, 'forgot_password.html', {'email_sent': True})
            else:
                return render(request, 'forgot_password.html', {'email_not_found': True})
        except Exception as e:
            return render(request, 'forgot_password.html', {'error': str(e)})
    return render(request, 'forgot_password.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return redirect('login')
            else:
                return render(request, 'password_reset_confirm.html', {'error': 'Passwords do not match'})
        return render(request, 'password_reset_confirm.html', {'valid_link': True})
    else:
        return render(request, 'password_reset_confirm.html', {'valid_link': False})

@login_required
def process_order(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        whatsapp_number = request.POST.get('whatsapp_number')
        quantity = int(request.POST.get('quantity'))
        address = request.POST.get('address')

        product = Product.objects.get(id=product_id)
        user = request.user

        # Create an order
        total_price = product.price * quantity
        order = Order.objects.create(
            user=user,
            product=product,
            whatsapp_number=whatsapp_number,
            quantity=quantity,
            address=address,
            total_price=total_price,
            status='Pending'
        )

        messages.success(request, 'Order processed successfully. The admin will contact you on WhatsApp.')
        return redirect('product_detail', pk=product.id)
    else:
        return HttpResponse("Invalid request method")

# shop/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)
    total_spent = sum(order.total_price for order in orders)
    return render(request, 'shop/profile.html', {'orders': orders, 'total_spent': total_spent})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
    return redirect('profile')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if cart_item.cart.user == request.user:
        cart_item.delete()
    return redirect('view_cart')

@login_required
def view_cart(request):
    user = request.user
    cart_items = CartItem.objects.filter(cart__user=user)
    for item in cart_items:
        item.total_price = item.product.price * item.quantity
    cart_is_empty = not cart_items.exists()
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'cart_is_empty': cart_is_empty})

@login_required
def checkout(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = cart.cartitem_set.all()

    if request.method == 'POST':
        whatsapp_number = request.POST.get('whatsapp_number')
        address = request.POST.get('address')

        for item in cart_items:
            Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                whatsapp_number=whatsapp_number,
                address=address,
                total_price=item.product.price * item.quantity,
                status='pending'
            )
        # Clear the cart after placing the order
        cart_items.delete()
        return redirect('order_confirmation')  # Assuming you have an order confirmation view
    
    return render(request, 'shop/checkout.html', {'cart_items': cart_items})

@login_required
def order_confirmation(request):
    return render(request, 'shop/order_confirmation.html')

@login_required
def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber, created = Subscriber.objects.get_or_create(user=request.user)
            subscriber.email = form.cleaned_data['email']
            subscriber.save()
            messages.success(request, 'You have successfully subscribed to the newsletter!')
            return redirect('home')
    else:
        form = SubscriberForm()
    return redirect('home')

@login_required
def unsubscribe(request):
    Subscriber.objects.filter(user=request.user).delete()
    messages.success(request, 'You have successfully unsubscribed from the newsletter.')
    return redirect('home')

def send_verification_email(subscriber):
    subject = 'Verify your email for our Newsletter'
    message = f'Click the link to verify your email: {settings.SITE_URL}/verify/{subscriber.verification_code}/'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [subscriber.email])

def verify_email(request, code):
    try:
        subscriber = Subscriber.objects.get(verification_code=code)
        subscriber.is_verified = True
        subscriber.verification_code = ''
        subscriber.save()
        return redirect('verification_success')
    except Subscriber.DoesNotExist:
        return redirect('verification_failed')

def send_newsletter(product):
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        send_mail(
            'New Product Added: {}'.format(product.name),
            'A new product has been added to our store:\n\n'
            'Name: {}\n'
            'Category: {}\n'
            'Price: {}\n'
            'Description: {}\n\n'
            'Check it out now!'.format(product.name, product.category, product.price, product.description),
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.email],
            fail_silently=False,
        )

@login_required
def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save()
            send_announcement_email(announcement)
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'create_announcement.html', {'form': form})

def send_announcement_email(announcement):
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        try:
            subject = f'New Announcement: {announcement.headline}'
            message = render_to_string('announcement_email.html', {
                'headline': announcement.headline,
                'content': announcement.content,
                'image_url': announcement.image.url if announcement.image else None
            })
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [subscriber.email], html_message=message)
            logger.info(f'Email sent to {subscriber.email}')
        except Exception as e:
            logger.error(f'Error sending email to {subscriber.email}: {e}')

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def custom_admin_dashboard(request):
    orders_count = Order.objects.count()
    unseen_orders_count = Order.objects.filter(status='pending').count()
    context = {
        'orders_count': orders_count,
        'unseen_orders_count': unseen_orders_count,
    }
    return render(request, 'custom_index.html', context)

@login_required
def order_details(request):
    orders = Order.objects.all()
    unseen_orders = orders.filter(status='pending')
    for order in unseen_orders:
        order.status = 'seen'
        order.save()
    return render(request, 'order_details.html', {'orders': orders})

def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.status = request.POST.get('status')
        order.save()
        return redirect('order_details')
    return redirect('order_details')


