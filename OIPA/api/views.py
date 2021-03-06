from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

from django.db import connections
from django.db import OperationalError


@api_view(('GET',))
def welcome(request, format=None):
    """
    ## REST API

    The REST API provides programmatic access to read (and soon also write) IATI data.
    The REST API responses are available in JSON.

    ## Available endpoints

    * Activities: [`/api/activities`](/api/activities)

    * Publishers: [`/api/publishers`](/api/publishers)

    * Organisations: [`/api/organisations`](/api/organisations)

    * Results aggregations: [`/api/results/aggregations`](/api/results/aggregations)

    * Locations: [`/api/locations`](/api/locations)

    * Cities: [`/api/cities`](/api/cities)

    * Datasets: [`/api/datasets`](/api/datasets)

    * Sectors: [`/api/sectors`](/api/sectors)

    * Countries: [`/api/countries`](/api/countries)

    * Transactions: [`/api/transactions`](/api/transactions)

    * Regions: [`/api/regions`](/api/regions)

    * Budget aggregations: [`/api/budgets/aggregations`](/api/budgets/aggregations)

    * Codelists: [`/api/publishers`](/api/codelists)
    
    * Chains: [`/api/chains`](/api/chains)

    """
    return Response({
        'endpoints': {
            'cities': reverse(
                'cities:city-list',
                request=request,
                format=format),
            'regions': reverse(
                'regions:region-list',
                request=request,
                format=format),
            'activities': reverse(
                'activities:activity-list',
                request=request,
                format=format),
            'countries': reverse(
                'countries:country-list',
                request=request,
                format=format),
            'sectors': reverse(
                'sectors:sector-list',
                request=request,
                format=format),
            'organisations': reverse(
                'organisations:organisation-list',
                request=request,
                format=format),
            'transactions': reverse(
                'transactions:transaction-list',
                request=request,
                format=format),
            'publishers': reverse(
                'publishers:publisher-list',
                request=request,
                format=format),
            'datasets': reverse(
                'datasets:dataset-list',
                request=request,
                format=format),
            'locations': reverse(
                'locations:location-list',
                request=request,
                format=format),
            'results': reverse(
                'results:result-aggregations',
                request=request,
                format=format),
            'budgets': reverse(
                'budgets:budget-aggregations',
                request=request,
                format=format),
            'codelists': reverse(
                'codelists:codelist-meta-list',
                request=request,
                format=format),
            'chains': reverse(
                'chains:chain-list',
                request=request,
                format=format),
        }
    })


@api_view(('GET',))
def health_check(request, format=None):
    """
    Performs an API health check
    """
    okay = True

    conn = connections['default']
    try:
        c = conn.cursor()
    except OperationalError:
        okay = False

    if okay is False:
        return Response(status=500)

    return Response(status=200)
