from django.db import models
from django.core.validators import MaxLengthValidator
import datetime


class Category(models.Model):
    image = models.ImageField(upload_to='category/', blank=True, null=True)
    category = models.CharField(max_length=50, unique=True, verbose_name="Категория")

    def __str__(self):
        return self.category

class Marka(models.Model):
    marka = models.CharField(max_length=50, unique=True, verbose_name="марка")

    def __str__(self):
        return self.marka

class Product(models.Model):
    CHOICE_NEW = 'Новый'
    CHOICE_USED = 'Б/У'
    
    CHOICE_OPTIONS = [
        (CHOICE_NEW, 'Новый'),
        (CHOICE_USED, 'БУ'),
    ]

    image1 = models.ImageField(upload_to="cards/")
    image2 = models.ImageField(upload_to="cards/", blank=True, null=True)
    image3 = models.ImageField(upload_to="cards/", blank=True, null=True)
    image4 = models.ImageField(upload_to="cards/", blank=True, null=True)
    title = models.CharField(max_length=30)
    price = models.PositiveIntegerField()
    description = models.TextField(validators=[MaxLengthValidator(300)])
    artikul = models.CharField(max_length=30, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    in_stock = models.BooleanField(default=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    spare_part_number = models.CharField(max_length=50)
    generation = models.CharField(max_length=50)
    choice = models.CharField(
        max_length=6,
        choices=CHOICE_OPTIONS,
        default=CHOICE_NEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    marka = models.CharField(max_length=50, verbose_name='марка', blank=True, null=True)  

    def __str__(self):
        return self.title



