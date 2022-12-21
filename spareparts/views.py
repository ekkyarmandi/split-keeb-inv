from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views import View

from django.http import JsonResponse
from django.db.models import Sum
from django.contrib import messages

from build_log.models import ItemOut, BuildLog

from .models import *
from datetime import datetime
import re


### Other Functions
def get_platform(link):
    pattern = '(?<=http\:\/\/)(.*?)(?=\/)|(?<=https\:\/\/)(.*?)(?=\/)|www[a-z\.]+'
    result = re.search(pattern,link)
    if result:
        return result.group()
    else:
        return 'offline'

class OrderFormData():
    ''' Collect order data based on post form '''

    def __init__(self,post):
        self.date=self.check_date(post.get("order-date"))
        self.arrival=self.check_date(post.get("arrival-date"))
        self.shipping_fee=float(post.get("shipping-cost",0))
        self.total_tax=int(post.get("tax",0))
        self.is_usd = True if post.get("is-usd") == "on" else False
        self.usd_to_idr = float(post.get("usd-to-idr",0))
        self.names=post.getlist("item-name")
        self.kinds=post.getlist("item-kind")
        self.links=post.getlist("item-link")
        self.price=list(map(float,post.getlist("item-price")))
        self.qty=list(map(int,post.getlist("item-qty")))
        self.unit=list(map(int,post.getlist("item-unit")))
        self.price_perunit=list(map(float,post.getlist("price-perunit")))
        self.origin=post.get("shipping-origin")
        self.track_order_link=post.get("tracking-link","#")
        self.notes=post.get("order-notes")
        self.sum_product_price = 0
        self.arrival_days = 0
        self.total_order = 0
        # shopping_platform

        self.check_status()
        self.calculate_total_order()
        self.calculate_arrival_days()
        
    def check_date(self,date):
        try:
            return datetime.strptime(date,"%Y-%m-%d")
        except:
            return None

    def calculate_arrival_days(self):
        if self.arrival:
            self.arrival_days = (self.arrival-self.date).days

    def check_status(self):
        if self.arrival:
            self.status = "in_stock"
        else:
            self.status = "on_delivery"

    def calculate_total_order(self):

        ### calculate total product price
        self.sum_product_price = 0
        for p,q in zip(self.price,self.qty):
            self.sum_product_price += int(p) * int(q)

        ### calculate total order
        self.total_order = sum([
            self.sum_product_price,
            self.shipping_fee,
            self.total_tax,
        ])

    def __str__(self):
        return ""
        
class Home(ListView):
    template_name = "home.html"
    model = Order

    def get_queryset(self):
        return Order.objects.filter(arrival=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        return context

class Summary(View):
    template_name = "summary.html"
    context = {
        "title": "Summary",
        "summary_page": True,
        "starting": datetime(2022,9,13)
    }

    def get(self, request):
        items = ItemOut.objects.all()
        sum_of_order = Order.objects.all().aggregate(Sum("total_order")).get("total_order__sum",0)
        wasted = [i.sparepart.price_perunit*i.stock_out for i in items if not i.build_log and not i.personal_use]
        on_build = [i.sparepart.price_perunit*i.stock_out for i in items if i.build_log and not i.build_log.is_sold]
        sold_out = [i.sparepart.price_perunit*i.stock_out for i in items if i.build_log and i.build_log.is_sold]
        personal_use = [i.sparepart.price_perunit*i.stock_out for i in items if i.personal_use]
        profit = BuildLog.objects.filter(is_sold=True).aggregate(Sum("sold_price")).get("sold_price__sum",0)
        
        self.context.update({
            "total_order" : sum_of_order,
            "on_build" : sum(on_build),
            "sold_out" : sum(sold_out),
            "personal_use": sum(personal_use),
            "wasted_item" : sum(wasted),
            "loss": sum_of_order - profit - sum(personal_use),
            "earned": profit,
            "profit": profit - sum(sold_out),
        })
        return render(request, self.template_name, self.context)

class OrdersView(ListView):
    template_name = "orders.html"
    model = Order

    def get_queryset(self):
        return Order.objects.all().order_by('arrival')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Orders'
        context['order_page'] = True
        context['total_order'] = Order.objects.all().aggregate(Sum('total_order')).get("total_order__sum",0)
        return context

class NewOrderView(View):
    template_name = "new_order.html"

    def get(self, request, *args, **kwargs):
        spareparts = Sparepart.objects.all()
        kinds = list(dict.fromkeys([item.kind for item in spareparts]))
        context = {
            'title': "Add New Order",
            'kinds': kinds,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        # get new order data
        f = OrderFormData(request.POST)

        ## Create the order object
        order = Order.objects.create(
            date=f.date,
            arrival=f.arrival,
            origin=f.origin,
            sum_product_price=f.sum_product_price,
            is_usd=f.is_usd,
            usd_to_idr=f.usd_to_idr,
            shipping_fee=f.shipping_fee,
            total_tax=f.total_tax,
            track_order_link=f.track_order_link,
            arrival_days=f.arrival_days,
            total_order=f.total_order,
            notes=f.notes,
        )

        # Create the spareparts object
        for i, name in enumerate(f.names):
            q = f.qty[i]
            u = f.unit[i]
            p = f.price[i]
            pp = f.price_perunit[i]
            sparepart = Sparepart.objects.create(
                name=name,
                kind=f.kinds[i].upper(),
                in_stock=q*u,
                price=p,
                price_perunit=pp,
                link=f.links[i],
                status=f.status,
            )

            # Create the OrderSpareparts object
            OrderSparepart.objects.create(
                order=order,
                sparepart=sparepart,
                unit=u,
                qty=q,
                price=p,
            )

        return redirect("home")

class EditOrderView(View):
    template_name = "edit_order.html"

    def get(self, request, pk):
        order = Order.objects.get(id=pk) 
        invoices = order.ordersparepart_set.all()
        kinds = list(dict.fromkeys([s.kind for s in Sparepart.objects.all()]))
        context = {
            "title": "#" + str(pk) + " Edit Order",
            "order": order,
            "kinds": kinds,
            "invoices": invoices,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        order = Order.objects.get(id=pk)
        formdata = OrderFormData(request.POST)

        ### update order
        order.date=formdata.date
        order.arrival=formdata.arrival
        order.arrival_days=formdata.arrival_days
        order.origin=formdata.origin
        order.is_usd=formdata.is_usd
        order.usd_to_idr=formdata.usd_to_idr
        order.sum_product_price=formdata.sum_product_price
        order.shipping_fee=formdata.shipping_fee
        order.total_tax=formdata.total_tax
        order.total_order=formdata.total_order
        order.track_order_link=formdata.track_order_link
        order.notes=formdata.notes
        order.save()

        sparepart_ids = []
        for i,invoice in enumerate(order.ordersparepart_set.all()):
            p = formdata.price[i]
            q = formdata.qty[i]
            u = formdata.unit[i]
            pp = formdata.price_perunit[i]

            ### update invoices
            invoice.price = p
            invoice.qty = q
            invoice.unit = u
            invoice.save()

            ### update spareparts
            sparepart_ids.append(invoice.sparepart.id)
            invoice.sparepart.name = formdata.names[i]
            invoice.sparepart.kind = formdata.kinds[i]
            invoice.sparepart.link = formdata.links[i]
            invoice.sparepart.price = p
            invoice.sparepart.in_stock = q * u
            invoice.sparepart.perunit_price = pp
            invoice.sparepart.status = formdata.status
            invoice.sparepart.save()

        ### update sparepart stock
        spareparts = Sparepart.objects.filter(id__in=sparepart_ids)
        for sp in spareparts:
            agg = ItemOut.objects.filter(sparepart=sp).aggregate(Sum("stock_out"))
            total_stock_out = agg.get("stock_out__sum",0)
            if total_stock_out:
                sp.in_stock -= total_stock_out
                sp.save()
        
        return redirect("orders")

def delete_order(request,pk):
    """ Delete order including the spareparts and the invoices"""

    order = Order.objects.get(id=pk)
    invoices = order.ordersparepart_set.all()
    for sp in invoices:
        sp.sparepart.delete()
        sp.delete()
    order.delete()
    return redirect("orders")

class SparepartsView(ListView):
    template_name = "spareparts.html"
    model = Sparepart

    def get_queryset(self):
        items = []
        for item in Sparepart.objects.exclude(in_stock=0).order_by('kind'):
            items.append(item)
        for item in Sparepart.objects.filter(in_stock=0).order_by('kind'):
            items.append(item)
        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iventories'
        context['inventory_page'] = True
        return context
        
### Order & Sparepart view
def edit_sparepart(request, pk):
    sparepart = Sparepart.objects.get(id=pk)
    sparepart.name = request.POST.get("sparepart-name")
    sparepart.kind = request.POST.get("sparepart-kind")
    sparepart.save()
    return redirect("spareparts")

def update_arrival(request,pk):

    if request.method == "POST":

        # get the order
        order = Order.objects.get(order_id=pk)
        order.arrival = datetime.strptime(request.POST.get('arrival-date'),'%Y-%m-%d').date()
        order.calculate_arrival()
        order.save()

        # update the sparepart stock
        OrderSpareparts = order.OrderSparepart_set.prefetch_related()
        for OrderSparepart in OrderSpareparts:
            sparepart = OrderSparepart.related_sparepart
            sparepart.in_stock += OrderSparepart.qty*OrderSparepart.unit
            sparepart.save()

        return redirect('home')

### Add new sparepart view
def add_new_sparepart(request):

    if request.method == "GET":
        kinds = Sparepart.objects.all().values_list('kind',flat=True).distinct()
        kinds = list(filter(lambda s: s.strip() != "",kinds))
        context = {
            'title': 'Add new sparepart',
            'heading': 'Add New Sparepart',
            'description': 'Input spareparts manualy',
            'kinds': kinds,
        }
        return render(request, 'add_sparepart.html', context)

    elif request.method == "POST":

        ## get the post data
        data = request.POST

        ## get name and link for validation
        name = data.get("item-name")
        link = data.get("item-link")

        ## check the sparepart existence
        try:
            item = Sparepart.objects.get(name=name,link=link)
            messages.error(request, f'{name} has been exists in the database')
        except:
            item = Sparepart(
                name=name,
                link=link,
                kind=data.get("item-kind"),
                in_stock=int(data.get("item-stock",0)),
                price=int(data.get("item-price",0)),
                perunit_price=float(data.get("item-perunit-price",0.00)),
                description=data.get("item-description")
            )
            item.save()
            messages.success(request, f'{name} has been added to the database')

        # redirect the response
        return redirect('spareparts')

### API
def get_spareparts(request):
    spareparts = {part.sparepart_id:part.to_dict() for part in Sparepart.objects.all()}
    return JsonResponse(spareparts)

def get_sparepart(request,pk):

    if request.method == "GET":
        item = Sparepart.objects.get(sparepart_id=pk)
        kinds = Sparepart.objects.all().values_list('kind',flat=True).distinct()
        kinds = list(filter(lambda s: s.strip() != "",kinds))
        context = {
            'title': item.name,
            'heading': 'Edit Sparepart Data',
            'description': 'Modify existings sparepart data',
            'kinds': kinds,
            'sparepart': item
        }
        return render(request, 'add_sparepart.html', context)

    elif request.method == "POST":
        data = request.POST
        item = Sparepart.objects.get(sparepart_id=pk)
        item.name = data.get("item-name")
        item.link = data.get("item-link")
        item.kind = data.get("item-kind")
        item.in_stock = int(data.get("item-stock",0))
        item.price = int(data.get("item-price",0))
        item.perunit_price = float(data.get("item-perunit-price",0.00))
        item.description = data.get("item-description","").strip()
        item.save()
        return redirect('spareparts')