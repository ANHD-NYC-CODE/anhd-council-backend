from datasets import models as d_models


def queryset_by_housingtype(housingtype):
    switcher = {
        "rent-stabilized": d_models.Properties.objects.all(),
        "rent-regulated": d_models.Properties.objects.all(),
        "small-homes": d_models.Properties.objects.all(),
        "market-rate": d_models.Properties.objects.all(),
        "public-housing": d_models.Properties.objects.all(),
    }

    return switcher.get(housingtype, [])
