import django_filters
from django.db.models import F
from .models import Product, Category


class ProductsFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr='icontains')
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt', method="filter_price_gt")
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt', method="filter_price_lt")
    has_discount = django_filters.BooleanFilter(field_name='discount', method="filter_has_discount")
    category = django_filters.ModelMultipleChoiceFilter(
        field_name="category",
        null_label="Uncategorized",
        queryset=Category.objects.all()
    )

    def filter_has_discount(self, queryset, field_name, value):

        if value:
            return queryset.filter(discount__gt=0)
        return queryset

    def filter_price_gt(self, queryset, field_name, value):

        if value:
            return queryset.annotate(db_price_with_discount=F("price") - F("price") * F("discount") / 100).filter(db_price_with_discount__gt=value)
        return queryset

    def filter_price_lt(self, queryset, fields_name, value):
        if value:
            return queryset.annotate(db_price_with_discount=F("price") - F("price") * F("discount") / 100).filter(db_price_with_discount__lt=value)
        return queryset


    class Meta:
        model = Product
        fields = [
            'name',
            'category',
        ]
