from django.db import models

from spareparts.models import Sparepart

class BuildLog(models.Model):
    build_date = models.DateField(null=True,blank=True)
    title = models.CharField(max_length=126)
    material_cost = models.FloatField(default=0.00)
    build_hours = models.IntegerField(default=0,null=True,blank=True)
    is_sold = models.BooleanField(default=False)
    sold_price = models.IntegerField(default=0)
    service_fee = models.IntegerField(default=200000)
    notes = models.TextField(default="")

    class Meta:
        ordering = ["build_date"]

    def __str__(self):
        build_date = self.build_date.strftime("%d/%m/%Y")
        return f"<BuildLog id={self.id} title='{self.title}' build_date={build_date} material_cost=Rp {self.material_cost:,.0f}>"

class ItemOut(models.Model):
    out_date = models.DateField(null=True, blank=True)
    sparepart = models.ForeignKey(Sparepart, on_delete=models.CASCADE)
    build_log = models.ForeignKey(BuildLog, null=True, blank=True, on_delete=models.CASCADE)
    stock_out = models.IntegerField(default=0)
    personal_use = models.BooleanField(default=False)
    notes = models.TextField(default="-")

    def __str__(self):
        build_id = "#"+str(self.build_log.id) if self.build_log else "None"
        return f"<ItemOut out_date={self.out_date.strftime('%d-%m-%Y')} sparepart='{self.sparepart.name}' related_build={build_id} stock_out={self.stock_out} stock_left={self.sparepart.in_stock} is_personal_use={self.personal_use}>"

class SoldOut(models.Model):
    title = models.CharField(max_length=127)
    build_log = models.ForeignKey(BuildLog, on_delete=models.RESTRICT)
    is_sold = models.BooleanField(default=False)
    markup = models.FloatField(default=0.4)
    material_cost = models.IntegerField(default=0)
    service_cost = models.IntegerField(default=200000)

    def __str__(self):
        return f"<Product title={self.title} build_log={self.build_log.title} material_cost=Rp {self.material_cost:,.2f} >"