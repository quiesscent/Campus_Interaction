# filters.py
from django_filters import rest_framework as filters
from .models import Event
from django.utils import timezone


class EventFilter(filters.FilterSet):
    status = filters.CharFilter(method='filter_by_status')
    campus = filters.CharFilter(field_name='campus__campus')

    class Meta:
        model = Event
        fields = ['event_type', 'is_public', 'campus']

    def filter_by_status(self, queryset, name, value):
        now = timezone.now()
        if value == 'upcoming':
            return queryset.filter(start_date__gt=now)
        elif value == 'ongoing':
            return queryset.filter(start_date__lte=now, end_date__gte=now)
        elif value == 'completed':
            return queryset.filter(end_date__lt=now)
        return queryset