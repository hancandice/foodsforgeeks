from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path('', views.index, name="homepage"),
    path('checkout/', views.CheckoutView.as_view(), name="checkout"),
    path('order-summary/', views.OrderSummaryView.as_view(), name="order-summary"),
    path('product/<slug>/', views.ItemDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>/', views.add_to_cart, name="add-to-cart"),
    path('add-coupon/', views.AddCouponView.as_view(), name="add-coupon"),
    path('remove-from-cart/<slug>/',
         views.remove_from_cart, name="remove-from-cart"),
    path('remove-item-from-cart/<slug>/',
         views.remove_single_item_from_cart, name="remove-single-item-from-cart"),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name="payment"),
    path("request-refund/", views.RequestRefundView.as_view(), name="request-refund")
]
