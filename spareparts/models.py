from django.db import models

class Order(models.Model):
    date = models.DateField()
    arrival = models.DateField(null=True,blank=True)
    arrival_days = models.IntegerField(null=True,blank=True,default=0)
    origin = models.CharField(max_length=100)
    shopping_platform = models.CharField(max_length=100,null=True,blank=True,default='offline')
    is_usd = models.BooleanField(default=False)
    usd_to_idr = models.FloatField(default=0)
    shipping_fee = models.FloatField(default=0)
    total_tax = models.IntegerField(default=0)
    sum_product_price = models.FloatField(default=0)
    total_order = models.IntegerField(default=0)
    track_order_link = models.CharField(default="#",max_length=700)
    notes = models.TextField(default="",null=True,blank=True)

    def tax_percentage(self):
        if self.is_usd:
            return 100*self.total_tax/(self.sum_product_price*self.usd_to_idr)
        else:
            return 100*self.total_tax/self.sum_product_price

    def title(self):
        title = [
            self.date.strftime('%d/%m/%Y'),
            self.shopping_platform
        ]
        title = list(map(str,title))
        return " ".join(title)

    def calculate_total(self):

        ### calculate the total product price
        product_price = [p.price*p.qty for p in self.ordersparepart_set.all()]
        self.sum_product_price = sum(product_price)
        
        ### calculate the total order (including shipping fee, tax, and total product price)
        if self.is_usd:
            self.total_order = sum([
                self.sum_product_price * self.usd_to_idr,
                self.shipping_fee * self.usd_to_idr,
                self.total_tax
            ])
        else:
            self.total_order = sum([
                self.sum_product_price,
                self.shipping_fee,
                self.total_tax
            ])
        
        ### calculate perunit price
        for invoice in self.ordersparepart_set.all():
            perc = (invoice.price * invoice.qty) / self.sum_product_price
            # invoice.sparepart.in_stock = invoice.qty * invoice.unit
            invoice.sparepart.price_perunit = (perc*self.total_order)/invoice.sparepart.in_stock
            invoice.sparepart.price_perunit = round(invoice.sparepart.price_perunit,2)
            invoice.sparepart.status = "in_stock" if self.arrival else "on_delivery"
            invoice.sparepart.save()

    def __str__(self):
        order_date = self.date.strftime("%d/%m/%Y")
        items = self.ordersparepart_set.all().count()
        return f"<Order #{self.id:02d} date={order_date} platform='{self.shopping_platform}' origin='{self.origin}' n_item={items}>"

class Sparepart(models.Model):

    STOCK_STATUS = [
        ('in_stock','In Stock'),
        ('out_of_stock','Out of Stock'),
        ('on_delivery','On Delivery'),
    ]

    added = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=125)
    kind = models.CharField(max_length=125, null=True, blank=True)
    in_stock = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    price_perunit = models.FloatField(default=0)
    link = models.CharField(default="#",max_length=700)
    status = models.CharField(default="on_delivery",max_length=15,choices=STOCK_STATUS)

    def to_dict(self):
        part_dict = {
            'id': self.sparepart_id,
            'name': self.name,
            'kind': self.kind,
            'in_stock': self.in_stock,
            'origin': self.invoice_set.first().related_order.shipping_origin,
            'price': self.price,
            'perunit_price': self.perunit_price,
            'link': self.link,
        }
        return part_dict

    def on_delivery(self):
        if self.invoice_set.last().related_order.arrival_date:
            return False
        else:
            return True

    class Meta:
        ordering = ['kind']

    def __str__(self):
        return self.name + f" (Rp {self.price_perunit:,.0f}/unit) [stock_left={self.in_stock}]"

class OrderSparepart(models.Model):
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE)
    sparepart = models.ForeignKey(Sparepart, null=True, on_delete=models.CASCADE)
    unit = models.IntegerField(default=0)
    qty = models.IntegerField(default=0)
    price = models.FloatField(default=0)

    class Meta:
        ordering = ['order__date','order']

    def __str__(self):
        order_date = self.order.date.strftime('%d/%m/%Y')
        curr = "$" if self.order.is_usd else "Rp"
        return f"<Invoice related_order={order_date}_#{self.order.id:02d} sparepart='{self.sparepart.name}' price={curr}{self.price:,.2f} qty={self.qty} qty_perunit={self.unit}>"