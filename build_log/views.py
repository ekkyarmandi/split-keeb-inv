from django.views.generic.list import ListView
from django.views.generic import View
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse

from spareparts.models import Sparepart

from .models import *
from .forms import *

class BuildLogForm():

    def __init__(self,post):
        self.date = self.format_date(post.get("build-date"))
        self.hours = int(post.get("build-hours"))
        self.title = post.get("build-title")
        self.notes = post.get("build-notes")
        self.spareparts = list(map(self.int,post.getlist("material-select")))
        self.kinds = post.getlist("material-kind")
        self.stock_left = list(map(self.int,post.getlist("material-stock-left")))
        self.stock_out = list(map(self.int,post.getlist("material-stock-out")))
        self.material_cost = 0
        self.zipped = zip(
            self.spareparts,
            self.stock_left,
            self.stock_out
        )
        self.calculate_material_cost()

    def format_date(self,date):
        return datetime.strptime(date,"%Y-%m-%d")

    def int(self,string):
        try:
            return int(string) 
        except:
            return 0

    def calculate_material_cost(self):
        self.material_cost = 0
        for pk,_,out in self.zipped:
            if pk not in ["None",0]:
                item = Sparepart.objects.get(id=pk)
                self.material_cost += float(item.price_perunit) * int(out)

class BuildLogView(ListView):
    template_name = "build_log/build_logs.html"
    context_object_name = "logs"
    model = BuildLog

    def get_queryset(self):
        return super().get_queryset().order_by("is_sold")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Build Logs"
        return context

class NewBuildLog(View):
    template_name = 'build_log/create_build_log.html'
    context = {'title': 'New Build'}

    def get(self, request):
        return render(request, self.template_name, self.context)

    def post(self, request):

        ### Get input values
        build = BuildLogForm(request.POST)

        ### Create New Build
        build_log = BuildLog.objects.create(
            build_date=build.date,
            title=build.title,
            notes=build.notes,
            build_hours=build.hours,
            material_cost=build.material_cost
        )

        ### Update Sparepart In Stock & Create Item Out
        spareparts = Sparepart.objects.filter(id__in=build.spareparts)
        for sparepart in spareparts:
            i = build.spareparts.index(sparepart.id)
            sparepart.in_stock = build.stock_left[i]
            sparepart.save()
            ItemOut.objects.create(
                out_date=build.date,
                sparepart=sparepart,
                build_log=build_log,
                stock_out=build.stock_out[i],
            )
        return redirect("build-logs")

class EditBuildLog(View):
    template_name = "build_log/edit_build_log.html"

    def get(self, request, pk):
        build_log = BuildLog.objects.prefetch_related('itemout_set').get(id=pk)
        kinds = list(dict.fromkeys([s.kind for s in Sparepart.objects.all()]))
        context = {
            'title': '#'+str(build_log.id)+' Edit Build Log',
            'build_log': build_log,
            'kinds': kinds,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):

        ### Update Build Log
        build = BuildLogForm(request.POST)
        build_log = BuildLog.objects.get(id=pk)
        build_log.title = build.title
        build_log.build_date = build.date
        build_log.build_hours = build.hours
        build_log.material_cost = build.material_cost
        build_log.notes = build.notes
        build_log.save()

        ### Update Sparepart In Stock and Item Out
        ids = [int(_id) for _id in build.spareparts if _id not in ["None",0]]
        spareparts = Sparepart.objects.filter(id__in=ids)
        item_outs = [i.sparepart.id for i in ItemOut.objects.filter(build_log=build_log)]
        for sparepart in spareparts:
            i = ids.index(sparepart.id) + 1

            ### Update if Exists in ItemOut Table
            if sparepart.id in item_outs:
                item = ItemOut.objects.get(build_log=build_log,sparepart=sparepart)
                if item.stock_out != build.stock_out[i]:
                    item.stock_out = build.stock_out[i]
                    item.save()

            ### Create new entry in ItemOut Table
            else:
                ItemOut.objects.create(
                    out_date=build.date,
                    sparepart=sparepart,
                    build_log=build_log,
                    stock_out=build.stock_out[i],
                )

            if sparepart.in_stock != build.stock_left[i]:
                sparepart.in_stock = build.stock_left[i]
                sparepart.save()

        ### Remove ItemOut if the item excluded from the Build Log
        items = ItemOut.objects.filter(build_log=build_log)
        for item in items:
            if item.sparepart.id not in ids:
                item.sparepart.in_stock += item.stock_out
                item.sparepart.save()
                item.delete()

        return redirect("build-logs")

def delete_build_log(request, pk):
    build_log = BuildLog.objects.prefetch_related("itemout_set").get(id=pk)
    for i in build_log.itemout_set.all():
        i.sparepart.in_stock += i.stock_out
        i.sparepart.save()
    build_log.delete()
    return redirect("build-logs")

def build_sold_out(request,pk):
    build_log = BuildLog.objects.get(id=pk)
    build_log.is_sold = True if request.POST.get("is-sold") else False
    build_log.sold_price = int(request.POST.get("sold-price",0))
    build_log.service_fee = int(request.POST.get("service-fee",0))
    build_log.save()
    return redirect("build-logs")

### Item Out View
class ItemOutView(View):
    template_name = "build_log/item_out.html"
    context = {
        "title": "Item Out Table",
        "form": ItemOutForm()
    }

    def get(self,request):
        self.context.update({"items": ItemOut.objects.all().order_by("out_date")})
        return render(request, self.template_name, self.context)

    def post(self,request):
        form = ItemOutForm(request.POST)
        sid = request.POST.get("sparepart")
        stock_out = int(request.POST.get("stock_out"))
        sparepart = Sparepart.objects.get(id=sid)
        if form.is_valid() and stock_out > 0:
            sparepart.in_stock -= stock_out
            sparepart.save()
            form.save()
        return redirect("item-out")

def cancel_item_out(request,pk):
    item = ItemOut.objects.get(id=pk)
    item.sparepart.in_stock += item.stock_out
    item.sparepart.save()
    item.delete()
    return redirect("item-out")

### API
def get_spareparts(request):
    spareparts = [s for s in Sparepart.objects.all() if s.in_stock > 0]
    kinds = {}
    for part in spareparts:
        k = part.kind
        p = part.__dict__
        p.pop("_state")
        _id = p.get("id")
        if part.kind not in kinds:
            kinds.update({k:{_id:p}})
        else:
            kinds[k].update({_id:p})
    return JsonResponse(kinds)