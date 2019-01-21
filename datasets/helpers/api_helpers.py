from datasets import models as d_models


def queryset_by_housingtype(queryset, housingtype):
    switcher = {
        "rent-stabilized": queryset.rentstab(),
        "rent-regulated": queryset.rentreg(),
        "small-homes": queryset.smallhome(),
        "market-rate": queryset.marketrate()
    }

    return switcher.get(housingtype, None)
