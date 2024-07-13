from django.contrib import admin
from django.utils.html import format_html
from .models import Product, CarouselItem, Comment, Rating, Reply, Order, Query, Subscriber, Announcement
from .views import send_newsletter

# Registering Product model with newsletter sending feature
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'featured', 'created_at')
    list_filter = ('category', 'featured', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # Only send newsletter for new products
            send_newsletter(obj)

# Registering CarouselItem model
@admin.register(CarouselItem)
class CarouselItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('id',)

# Registering Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'text', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__username', 'product__name')
    actions = ['delete_selected_comments']

    def delete_selected_comments(self, request, queryset):
        for comment in queryset:
            comment.delete()
    delete_selected_comments.short_description = 'Delete selected comments'

# Registering Rating model
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    pass

# Registering Reply model
@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    pass

# Registering Order model
from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'whatsapp_number', 'address', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__name', 'whatsapp_number', 'address')

admin.site.register(Order, OrderAdmin)

# Registering Query model
@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    pass

# Registering Subscriber model
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    pass

from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('headline', 'created_at')  # Ensure 'created_at' is correctly referenced
    ordering = ('-created_at',)  # Ensure 'created_at' is correctly referenced

# shop/admin.py

# shop/admin.py

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Order

def custom_admin_dashboard(request):
    orders_count = Order.objects.count()
    context = {'orders_count': orders_count}
    return render(request, 'admin/custom_index.html', context)

class CustomAdminSite(admin.AdminSite):
    site_header = "Custom Admin"
    site_title = "Custom Admin Portal"
    index_title = "Welcome to the Custom Admin Portal"
    index_template = 'admin/custom_index.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(custom_admin_dashboard), name='custom_admin_dashboard'),
        ]
        return custom_urls + urls

admin_site = CustomAdminSite(name='custom_admin')


