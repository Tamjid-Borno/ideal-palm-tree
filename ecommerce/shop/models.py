from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils import timezone
from django.db import models
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('FASHION', 'Fashion'),
        ('ELECTRONICS', 'Electronics'),
        ('BEAUTY', 'Beauty'),
        ('OTHERS', 'Others'),
    )

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    featured = models.BooleanField(default=False)
    image = CloudinaryField('image')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_rating(self):
        return self.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0

    def __str__(self):
        return self.name

class CarouselItem(models.Model):
    image = CloudinaryField('image')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carousel Item {self.id}"

class Rating(models.Model):
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()

    def __str__(self):
        return f"{self.product.name} - {self.rating} stars"

class Comment(models.Model):
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.product.name}'

class Reply(models.Model):
    comment = models.ForeignKey(Comment, related_name='all_replies', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Reply by {self.user.username} on comment {self.comment.id}'

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('seen', 'Seen'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    whatsapp_number = models.CharField(max_length=15)  # Add this field
    address = models.CharField(max_length=255)

    def __str__(self):
        return f'Order {self.id} by {self.user}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

class Query(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name

class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email

from django.contrib.sites.models import Site

class Announcement(models.Model):
    headline = models.CharField(max_length=255)
    image = CloudinaryField('image', blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.send_announcement_email()

    def send_announcement_email(self):
        try:
            site = Site.objects.get_current()
        except Site.DoesNotExist:
            site = Site(domain='https://testinguwu.onrender.com', name='example')  # Fallback to a default site
        image_url = self.image.url if self.image else None

        subscribers = Subscriber.objects.all()
        for subscriber in subscribers:
            subject = f'Announcement: {self.headline}'
            message = render_to_string('announcement_email.html', {
                'headline': self.headline,
                'content': self.content,
                'image_url': image_url,
                'site': site
            })
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [subscriber.email], html_message=message)

