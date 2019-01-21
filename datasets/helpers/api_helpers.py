from datasets import models as ds


def properties_by_housingtype(request, queryset=None):
    if not queryset:
        queryset = ds.Property.objects

    if 'housingtype' in request.query_params:
        housingtype = request.query_params['housingtype']
    else:
        housingtype = None

    switcher = {
        "rent-stabilized": queryset.rentstab(),
        "rent-regulated": queryset.rentreg(),
        "small-homes": queryset.smallhome(),
        "market-rate": queryset.marketrate()
    }

    return switcher.get(housingtype, queryset)
