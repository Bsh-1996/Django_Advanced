from django.db import models
from accounts.models import User
from home.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'orders')
    paid = models.BooleanField(default= False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    discount = models.IntegerField(blank=True, null=True, default= None)


    class Meta:
        ordering = ('paid', '-updated')
    
    def __str__(self):
        return f'{self.user} - {str(self.id)}'
    
    def get_total_price(self):
        total = sum(item.get_cost() for item in self.items.all())
        if self.discount:
            discount_price = (self.discount / 100) * total
            return int(total - discount_price)
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete= models.CASCADE, related_name= 'items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name= 'order_items')
    price = models.IntegerField()
    quantity = models.IntegerField(default= 1)

    def __str__(self):
        return str(self.id)
    
    def get_cost(self):
        return self.price * self.quantity
    

class Coupan(models.Model):
    code = models.CharField(max_length= 10, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(90)])
    active = models.BooleanField(default= False)

    def __str__(self):
        return self.code
    
