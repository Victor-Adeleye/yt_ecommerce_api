from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    Product,
    Category,
    Cart,
    CartItem,
    ProductRating,
    Review,
    Wishlist,
    CustomerAddress,
    Order,
    OrderItem
)

# -------------------------------------------------
# Custom User admin
# -------------------------------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)


# -------------------------------------------------
# Product admin
# -------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "featured", "category")
    list_filter = ("featured", "category")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# -------------------------------------------------
# Category admin
# -------------------------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


# -------------------------------------------------
# Cart admin
# -------------------------------------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("cart_code", "user", "created_at", "updated_at")
    search_fields = ("cart_code", "user__username")
    list_filter = ("created_at",)
    readonly_fields = ("cart_code",)


# -------------------------------------------------
# Cart Item admin
# -------------------------------------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "sub_total_display")
    search_fields = ("cart__cart_code", "product__name")

    @admin.display(description="Sub Total")
    def sub_total_display(self, obj):
        return f"₦{obj.sub_total:,.2f}"


# -------------------------------------------------
# Product Rating admin
# -------------------------------------------------
@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ("product", "average_rating_display", "total_reviews_display")
    search_fields = ("product__name",)

    @admin.display(description="Average Rating")
    def average_rating_display(self, obj):
        return obj.average_rating

    @admin.display(description="Total Reviews")
    def total_reviews_display(self, obj):
        return obj.total_reviews


# -------------------------------------------------
# Review admin
# -------------------------------------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created", "updated")
    list_filter = ("rating", "created")
    search_fields = ("review", "user__username", "product__name")


# -------------------------------------------------
# Wishlist admin
# -------------------------------------------------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created")
    search_fields = ("user__username", "product__name")
    list_filter = ("created",)


# -------------------------------------------------
# Customer Address admin
# -------------------------------------------------
@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("customer", "email", "street", "city", "state", "phone", "created")
    search_fields = ("customer__username", "email", "city", "state")


# -------------------------------------------------
# Order admin
# -------------------------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("stripe_checkout_id", "customer_email", "amount", "currency", "status", "created")
    search_fields = ("stripe_checkout_id", "customer_email")
    list_filter = ("status", "created")


# -------------------------------------------------
# Order Item admin
# -------------------------------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity")
    search_fields = ("order__stripe_checkout_id", "product__name")
