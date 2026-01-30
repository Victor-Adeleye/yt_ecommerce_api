from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from decimal import Decimal

# ----------------------------
# Custom User Model
# ----------------------------
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.email


# ----------------------------
# Category Model
# ----------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="category_img", blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Automatically generate a unique slug based on category name."""
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


# ----------------------------
# Product Model
# ----------------------------
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="product_img", blank=True, null=True)
    featured = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="products",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Automatically generate a unique slug based on product name."""
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


# ----------------------------
# Cart Model
# ----------------------------
class Cart(models.Model):
    cart_code = models.CharField(max_length=11, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cart_code} ({self.user.username if self.user else 'No User'})"

    @property
    def total_amount(self):
        total = Decimal("0.00")
        for item in self.cartitems.all():
            total += item.sub_total
        return round(total, 2)


# ----------------------------
# Cart Item Model
# ----------------------------
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cartitems"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="items"
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product.name} in cart {self.cart.cart_code}"

    @property
    def sub_total(self):
        """Safely calculate subtotal as Decimal"""
        try:
            return Decimal(str(self.product.price)) * Decimal(self.quantity)
        except Exception:
            return Decimal("0.00")


# ----------------------------
# Review Model
# ----------------------------
class Review(models.Model):
    RATING_CHOICES = [
        (1, "1 = Poor"),
        (2, "2 = Fair"),
        (3, "3 = Good"),
        (4, "4 = Very Good"),
        (5, "5 = Excellent"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    review = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}"

    class Meta:
        unique_together = ["user", "product"]
        ordering = ["-created"]


# ----------------------------
# Product Rating Model
# ----------------------------
class ProductRating(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="rating")
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.average_rating} ({self.total_reviews} reviews)"


# ----------------------------
# Wishlist Model
# ----------------------------
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlists")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "product"]

    def __str__(self):
        return f"{self.user.username} → {self.product.name}"


# ----------------------------
# Customer Address Model
# ----------------------------
class CustomerAddress(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    email = models.EmailField()
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.city}"


# ----------------------------
# Order Model
# ----------------------------
class Order(models.Model):
    stripe_checkout_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    customer_email = models.EmailField()
    status = models.CharField(max_length=50, choices=[("Pending", "Pending"), ("Paid", "Paid")])
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.stripe_checkout_id} - {self.customer_email}"


# ----------------------------
# Order Item Model
# ----------------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"
