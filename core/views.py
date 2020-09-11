import stripe
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, View
from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address
from .forms import CheckoutForm, CouponForm, RefundForm
import random
import string

stripe.api_key = settings.STRIPE_SECRET_KEY
STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLISHABLE_KEY


def page_not_found(request, exception):

    # 404 Page not found

    return render(request, '404.html', {})


def internal_server_error(request):

    # 500 internal server error

    return render(request, '500.html', {})


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


def index(request):
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    sort = request.GET.get('sort', 'all')

    if sort == "starters":
        item_list = Item.objects.order_by(
            '-create_date').filter(category="Starters")
    elif sort == "main-dishes":
        item_list = Item.objects.order_by(
            '-create_date').filter(category="Main dishes")
    elif sort == "desserts":
        item_list = Item.objects.order_by(
            '-create_date').filter(category="Desserts")
    elif sort == "drinks":
        item_list = Item.objects.order_by(
            '-create_date').filter(category="Drinks")
    else:
        item_list = Item.objects.order_by('-create_date')
    if kw:
        item_list = item_list.filter(
            Q(title__icontains=kw) |
            Q(label__icontains=kw) |
            Q(description__icontains=kw)
        ).distinct()
    paginator = Paginator(item_list, 8)
    page_obj = paginator.get_page(page)
    context = {'page_obj': page_obj, 'page': page, 'kw': kw, 'sort': sort}
    return render(request, 'home.html', context)


def is_valid_form(values):
    valid = True
    for field in values: 
        if field == "":
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,
            }

            default_shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type="S",
                default_address=True,
                )

            if default_shipping_address_qs:
                context.update({"default_shipping_address": default_shipping_address_qs[0]})  

            default_billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type="B",
                default_address=True,
                )

            if default_billing_address_qs.exists():
                context.update({"default_billing_address": default_billing_address_qs[0]})    

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            return redirect("core:order-summary")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    default_shipping_address_qs = Address.objects.filter(
                                            user=self.request.user,
                                            address_type="S",
                                            default_address=True,
                                            )
                    if default_shipping_address_qs.exists():
                        shipping_address = default_shipping_address_qs[0]
                        order.shipping_address = shipping_address
                    else:
                        messages.info(self.request, "No default shipping address available.")    
                        return redirect("core:checkout")
                else:     
                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type="S",
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            ex_default_shipping_address_qs = Address.objects.filter(
                                            user=self.request.user,
                                            address_type="S",
                                            default_address=True,
                                            )
                            if ex_default_shipping_address_qs.exists():
                                ex_default_shipping_address=ex_default_shipping_address_qs[0]
                                ex_default_shipping_address.default_address=False
                                ex_default_shipping_address.save()

                            shipping_address.default_address=True
                            shipping_address.save()
                            order.shipping_address = shipping_address    

                    else:
                        messages.info(self.request, "Please fill in the required address fields.")
                        return redirect("core:checkout")    

                

                use_default_billing = form.cleaned_data.get('use_default_billing')

                same_with_billing_address = form.cleaned_data.get("same_with_billing_address")

                if same_with_billing_address:
                    billing_address = shipping_address
                    billing_address.default_address = False
                    billing_address.pk = None
                    billing_address.address_type="B"
                    billing_address.save()
                    use_default_billing = False
                    order.billing_address = billing_address

                elif use_default_billing:
                    default_billing_address_qs = Address.objects.filter(
                                            user=self.request.user,
                                            address_type="B",
                                            default_address=True,
                                            )
                    if default_billing_address_qs.exists():
                        billing_address = default_billing_address_qs[0]
                        order.billing_address = billing_address
                    else:
                        messages.info(self.request, "No default billing address available.")    
                        return redirect("core:checkout")
                else:       
                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type="B",
                        )
                        billing_address.save()
                        order.billing_address = billing_address

                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            ex_default_billing_address_qs = Address.objects.filter(
                                            user=self.request.user,
                                            address_type="B",
                                            default_address=True,
                                            )
                            if ex_default_billing_address_qs.exists():
                                ex_default_billing_address = ex_default_billing_address_qs[0]
                                ex_default_billing_address.default_address=False
                                ex_default_billing_address.save()

                            billing_address.default_address=True
                            billing_address.save()
                            order.billing_address = billing_address
                            
                    else:
                        messages.info(self.request, "Please fill in the required billing address fields.")   
                        return redirect("core:checkout")

                payment_option = form.cleaned_data.get('payment_option')
                order.payment_option = payment_option
                order.save()   


                if payment_option == "Stripe":
                    return redirect('core:payment', payment_option="stripe")
                elif payment_option == "PayPal":
                    return redirect('core:payment', payment_option="paypal")
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected.")
                    return redirect("core:checkout")

        except ObjectDoesNotExist:
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, request, payment_option, *args, **kwargs):
        if payment_option == "stripe":
            payment_option = "Stripe"
        elif payment_option == "paypal":
            payment_option = "PayPal"
        # order
        order = Order.objects.get(
            user=self.request.user, is_ordered=False, payment_option=payment_option)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address.")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            token = self.request.POST.get('stripeToken')
            amount = int(order.get_total() * 100)  # cents
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )
            # Create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order.is_ordered = True
            order.payment = payment
            # TODO: assign ref code
            order.ref_code = create_ref_code()
            order.save()

            order_items = order.items.all()
            order_items.update(is_ordered=True)
            for item in order_items:
                item.save()

            messages.success(
                self.request, f"Order was successful. Your order reference is {order.ref_code}")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            # Send an email to me.
            messages.warning(
                self.request, "A serious error occurred. We have been notified.")
            return redirect("/")
        except ObjectDoesNotExist:
            return redirect("core:order-summary")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order.")
            return render(self.request, 'order_summary.html')


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


def products(request):
    context = {'items': Item.objects.all()}
    return render(request, "products.html", context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        is_ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.success(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order.
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                is_ordered=False,
            )[0]
            order_item.delete()
            messages.warning(request, "This item was removed from your cart.")
            if order.items.count() == 0:
                order.delete()
            return redirect("core:order-summary")
        else:
            messages.warning(request, "This item was not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        messages.warning(request, "You do not have an active order.")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order.
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                is_ordered=False,
            )[0]
            if order_item.quantity >= 2:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                return redirect("core:order-summary")
            else:
                order_item.delete()
                messages.warning(
                    request, "This item was removed from your cart.")
                if order.items.count() == 0:
                    order.delete()
                return redirect("core:order-summary")
        else:
            messages.warning(request, "This item was not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        messages.warning(request, "You do not have an active order.")
        return redirect("core:product", slug=slug)


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if order:
                try:
                    coupon = Coupon.objects.get(code=code)
                except ObjectDoesNotExist:
                    messages.warning(
                        self.request, "This coupon does not exist.")
                    return redirect("core:checkout")
                order.coupon = coupon
                order.save()
                messages.success(self.request, "Successfully added coupon.")
                return redirect("core:checkout")
            else:
                messages.warning(
                    self.request, "You do not have an active order.")
                return redirect("core:order-summary")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form,
        }
        return render(self.request, "request-refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get("email")

            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request has been delivered.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.warning(
                    self.request, "This order does not exist.")
                return redirect("core:request-refund")

        else:
            context = {
                'form': form,
            }
            messages.warning(
                self.request, "Form is not valid.")
            return render(self.request, "request-refund.html", context)
