import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Cart, CartItem, Category, CustomerAddress,
    Order, OrderItem, Product, Review, Wishlist
)
from .serializers import (
    CartItemSerializer, CartSerializer, SimpleCartSerializer,
    CategoryDetailSerializer, CategoryListSerializer,
    CustomerAddressSerializer, OrderSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ReviewSerializer, WishlistSerializer, UserSerializer
)

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
User = get_user_model()


# ----------------------------
# PRODUCT VIEWS
# ----------------------------
@api_view(["GET"])
def product_list(request):
    products = Product.objects.filter(featured=True)
    return Response(ProductListSerializer(products, many=True).data)

@api_view(["GET"])
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return Response(ProductDetailSerializer(product).data)


# ----------------------------
# CATEGORY VIEWS
# ----------------------------
@api_view(["GET"])
def category_list(request):
    categories = Category.objects.all()
    return Response(CategoryListSerializer(categories, many=True).data)

@api_view(["GET"])
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return Response(CategoryDetailSerializer(category).data)


# ----------------------------
# CART VIEWS
# ----------------------------
@api_view(["POST"])
def add_to_cart(request):
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")
    if not cart_code or not product_id:
        return Response({"error": "cart_code and product_id are required"}, status=status.HTTP_400_BAD_REQUEST)

    cart, _ = Cart.objects.get_or_create(cart_code=cart_code)
    product = get_object_or_404(Product, id=product_id)
    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart)
    if not created:
        cartitem.quantity += 1
    else:
        cartitem.quantity = 1
    cartitem.save()
    return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_cartitem_quantity(request):
    cartitem = get_object_or_404(CartItem, id=request.data.get("item_id"))
    cartitem.quantity = int(request.data.get("quantity", 1))
    cartitem.save()
    return Response({
        "data": CartItemSerializer(cartitem).data,
        "message": "Cart item updated successfully"
    }, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_cartitem(request, pk):
    get_object_or_404(CartItem, id=pk).delete()
    return Response({"message": "Cart item deleted successfully"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_cart(request, cart_code):
    cart = Cart.objects.filter(cart_code=cart_code).first()
    if not cart:
        return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_cart_stat(request):
    cart_code = request.query_params.get("cart_code")
    cart = Cart.objects.filter(cart_code=cart_code).first()
    if not cart:
        return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(SimpleCartSerializer(cart).data, status=status.HTTP_200_OK)


@api_view(["GET"])
def product_in_cart(request):
    cart_code = request.query_params.get("cart_code")
    product_id = request.query_params.get("product_id")
    cart = Cart.objects.filter(cart_code=cart_code).first()
    if not cart:
        return Response({"product_in_cart": False})
    exists = CartItem.objects.filter(cart=cart, product_id=product_id).exists()
    return Response({"product_in_cart": exists}, status=status.HTTP_200_OK)


# ----------------------------
# REVIEW VIEWS
# ----------------------------
@api_view(["POST"])
def add_review(request):
    product = get_object_or_404(Product, id=request.data.get("product_id"))
    user = get_object_or_404(User, email=request.data.get("email"))
    if Review.objects.filter(product=product, user=user).exists():
        return Response({"error": "You already dropped a review"}, status=status.HTTP_400_BAD_REQUEST)
    review = Review.objects.create(
        product=product,
        user=user,
        rating=request.data.get("rating"),
        review=request.data.get("review")
    )
    return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
def update_review(request, pk):
    review = get_object_or_404(Review, id=pk)
    review.rating = request.data.get("rating", review.rating)
    review.review = request.data.get("review", review.review)
    review.save()
    return Response(ReviewSerializer(review).data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_review(request, pk):
    get_object_or_404(Review, id=pk).delete()
    return Response({"message": "Review deleted successfully"}, status=status.HTTP_200_OK)


# ----------------------------
# WISHLIST VIEWS
# ----------------------------
@api_view(["POST"])
def add_to_wishlist(request):
    user = get_object_or_404(User, email=request.data.get("email"))
    product = get_object_or_404(Product, id=request.data.get("product_id"))
    wishlist = Wishlist.objects.filter(user=user, product=product)
    if wishlist.exists():
        wishlist.delete()
        return Response({"message": "Wishlist deleted"}, status=status.HTTP_200_OK)
    wishlist_item = Wishlist.objects.create(user=user, product=product)
    return Response(WishlistSerializer(wishlist_item).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def my_wishlists(request):
    email = request.query_params.get("email")
    wishlists = Wishlist.objects.filter(user__email=email)
    return Response(WishlistSerializer(wishlists, many=True).data, status=status.HTTP_200_OK)


@api_view(["GET"])
def product_in_wishlist(request):
    email = request.query_params.get("email")
    product_id = request.query_params.get("product_id")
    exists = Wishlist.objects.filter(user__email=email, product_id=product_id).exists()
    return Response({"product_in_wishlist": exists}, status=status.HTTP_200_OK)


# ----------------------------
# SEARCH
# ----------------------------
@api_view(["GET"])
def product_search(request):
    query = request.query_params.get("query")
    if not query:
        return Response({"error": "No search query provided"}, status=status.HTTP_400_BAD_REQUEST)
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).distinct()
    return Response(ProductListSerializer(products, many=True).data, status=status.HTTP_200_OK)


# ----------------------------
# STRIPE CHECKOUT
# ----------------------------
@api_view(["POST"])
def create_checkout_session(request):
    cart_code = request.data.get("cart_code")
    email = request.data.get("email")

    if not cart_code or not email:
        return Response({"error": "cart_code and email are required"}, status=status.HTTP_400_BAD_REQUEST)

    cart = get_object_or_404(Cart, cart_code=cart_code)
    if cart.cartitems.count() == 0:
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    session = stripe.checkout.Session.create(
        customer_email=email,
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": item.product.name},
                    "unit_amount": int(item.product.price * 100),
                },
                "quantity": item.quantity,
            } for item in cart.cartitems.all()
        ],
        success_url="http://localhost:3000/success",
        cancel_url="http://localhost:3000/failed",
        metadata={"cart_code": cart.cart_code}
    )
    return Response({"url": session.url}, status=status.HTTP_200_OK)


# ----------------------------
# STRIPE WEBHOOK
# ----------------------------
@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] in ('checkout.session.completed', 'checkout.session.async_payment_succeeded'):
        session = event['data']['object']
        session = stripe.checkout.Session.retrieve(session["id"], expand=["customer_details"])
        cart_code = session.get("metadata", {}).get("cart_code")
        try:
            fulfill_checkout(session, cart_code)
        except Exception as e:
            print("⚠️ Webhook failed:", str(e))
            return HttpResponse(status=500)

    return HttpResponse(status=200)


# ----------------------------
# FULFILL CHECKOUT
# ----------------------------
def fulfill_checkout(session, cart_code):
    if Order.objects.filter(stripe_checkout_id=session["id"]).exists():
        print("Order already exists:", session["id"])
        return

    cart = get_object_or_404(Cart, cart_code=cart_code)

    order = Order.objects.create(
        stripe_checkout_id=session["id"],
        amount=session["amount_total"] / 100,
        currency=session["currency"],
        customer_email=session["customer_email"],
        status="Paid"
    )

    for item in cart.cartitems.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )

    cart.delete()
    print("✅ Order created:", order.id)
    print("Customer:", order.customer_email)
    print("Items:", order.items.count())


# ----------------------------
# TEST CREATE ORDER (No Stripe Needed)
# ----------------------------
@api_view(["POST"])
def test_create_order(request):
    cart_code = request.data.get("cart_code")
    email = request.data.get("email")
    if not cart_code or not email:
        return Response({"error": "cart_code and email required"}, status=status.HTTP_400_BAD_REQUEST)

    session_id = f"cs_test_manual_{cart_code}"
    cart = get_object_or_404(Cart, cart_code=cart_code)
    amount_total = sum(item.product.price * item.quantity for item in cart.cartitems.all())

    fake_session = {
        "id": session_id,
        "amount_total": int(amount_total * 100),
        "currency": "usd",
        "customer_email": email,
        "metadata": {"cart_code": cart.cart_code}
    }

    fulfill_checkout(fake_session, cart_code)
    return Response({"message": "Order created manually"}, status=status.HTTP_200_OK)


# ----------------------------
# USERS / ORDERS / ADDRESS
# ----------------------------
@api_view(["POST"])
def create_user(request):
    password = request.data.pop("password", None)
    user = User.objects.create_user(**request.data)
    if password:
        user.set_password(password)
        user.save()
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def existing_user(request, email):
    exists = User.objects.filter(email=email).exists()
    return Response({"exists": exists}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_orders(request):
    email = request.query_params.get("email")
    orders = Order.objects.filter(customer_email=email)
    return Response(OrderSerializer(orders, many=True).data, status=status.HTTP_200_OK)


@api_view(["POST"])
def add_address(request):
    customer = get_object_or_404(User, email=request.data.get("email"))
    address, _ = CustomerAddress.objects.get_or_create(customer=customer)
    for field in ["email", "street", "city", "state", "phone"]:
        setattr(address, field, request.data.get(field))
    address.save()
    return Response(CustomerAddressSerializer(address).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_address(request):
    address = CustomerAddress.objects.filter(customer__email=request.query_params.get("email")).last()
    if not address:
        return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(CustomerAddressSerializer(address).data, status=status.HTTP_200_OK)
