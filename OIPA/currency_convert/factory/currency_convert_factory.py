from factory.django import DjangoModelFactory
from currency_convert.models import MonthlyAverage
from iati_codelists.factory.codelist_factory import CurrencyFactory
from factory import SubFactory
from decimal import Decimal

class MonthlyAverageFactory(DjangoModelFactory):
    class Meta:
        model = MonthlyAverage

    currency = SubFactory(CurrencyFactory, code="EUR", name="Euro")
    month = 1994
    year = 1
    value = Decimal(1.5)
