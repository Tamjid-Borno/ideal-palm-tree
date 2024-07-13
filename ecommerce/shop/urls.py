from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import (
    home, product_list, about_us, contact_us, delete_comment,
    product_by_category, ProductViewSet, rate_product, add_rating,
    product_detail, send_verification_code, register, user_login,
    user_logout, forgot_password, password_reset_confirm, checkout,
    process_order, profile, cancel_order, view_cart, order_confirmation, verify_email, subscribe, create_announcement,  unsubscribe, custom_admin_dashboard, order_details
)

from . import views
from shop.admin import admin_site

router = DefaultRouter()
router.register(r'api/products', ProductViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('products/', product_list, name='product_list'),
    path('about/', about_us, name='about_us'),
    path('contact/', contact_us, name='contact_us'),
    path('delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('category/<str:category>/', product_by_category, name='product_by_category'),
    path('rate_product/<int:product_id>/', rate_product, name='rate_product'),
    path('add_rating/<int:product_id>/', add_rating, name='add_rating'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('send_verification_code/', send_verification_code, name='send_verification_code'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('order_confirmation/', order_confirmation, name='order_confirmation'),
    path('process_order/', process_order, name='process_order'),
    path('profile/', views.profile, name='profile'),
    path('profile/cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  # D
    path('subscribe/', subscribe, name='subscribe'),
    path('verify/<str:code>/', verify_email, name='verify_email'),
    path('create_announcement/', create_announcement, name='create_announcement'),
    path('unsubscribe/', unsubscribe, name='unsubscribe'),
    path('grappelli/', include('grappelli.urls')),
    path('custom_admin/', custom_admin_dashboard, name='custom_admin_dashboard'),
    path('order_details/', order_details, name='order_details'),
    path('order_details/update_status/<int:order_id>/', views.update_order_status, name='update_order_status'),

]


urlpatterns += router.urls
