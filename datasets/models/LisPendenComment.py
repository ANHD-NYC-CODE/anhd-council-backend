from django.db import models
from datasets.utils.BaseDatasetModel import BaseDatasetModel
from core.utils.transform import from_csv_file_to_gen, with_bbl
from datasets.utils.validation_filters import is_null
from datasets import models as ds
from django.dispatch import receiver
from django.db.models import Count, OuterRef, Q, Subquery
from datasets.utils import dates
from django.db.models.functions import Coalesce
from datetime import datetime, timezone


import logging

logger = logging.getLogger('app')

# Instructions:
# 1) merge all boroughs into single file - lp_lispendens_comments_<month><year>.csv - use these headers: KEY,BBL,ENTEREDDATE,ZIP,BC,FILEDDATE,INDEX,DEBTOR,CR,ATTORNEY,Third Party,SAT DATE,SAT TYPE,DISP 2) upload file to app 3) update


class LisPendenComment(BaseDatasetModel, models.Model):
    key = models.ForeignKey('LisPenden', db_column='key', db_constraint=False,
                            on_delete=models.SET_NULL, null=True, blank=False)
    datecomments = models.TextField(blank=True, null=True)

    @classmethod
    def pre_validation_filters(self, gen_rows):
        for row in gen_rows:
            if is_null(row['key']):
                continue
            yield row

    # trims down new update files to preserve memory
    # uses original header values
    @classmethod
    def update_set_filter(self, csv_reader, headers):
        return csv_reader

    @classmethod
    def transform_self(self, file_path, update=None):
        return self.pre_validation_filters(from_csv_file_to_gen(file_path, update))

    @classmethod
    def mark_lispenden_foreclosures(self):
        keys = set()
        for comment in self.objects.prefetch_related('key').all():
            # search for word foreclosure

            if comment.key_id in keys:
                continue
            if 'foreclosure' in comment.datecomments.lower():
                related_comments = self.objects.prefetch_related('key').filter(key=comment.key_id)
                # search for word 'mortgage' in all comments related to the lispenden
                for related_comment in related_comments:
                    if 'mortgage' in related_comment.datecomments.lower():
                        try:
                            keys.add(comment.key_id)
                        except Exception as e:
                            logger.debug("Foreclosure Key not found {}".format(comment.key_id))

        ds.LisPenden.objects.filter(key__in=keys).update(type='foreclosure')
        logger.debug("Marked {} foreclosures".format(len(keys)))

    @classmethod
    def seed_or_update_self(self, **kwargs):
        logger.debug("Seeding/Updating {}", self.__name__)

        self.seed_or_update_from_set_diff(**kwargs)
        self.mark_lispenden_foreclosures()
        self.annotate_properties()

    @classmethod
    def annotate_properties(self):
        count = 0
        records = []
        logger.debug('annotating properties for: {}'.format(self.__name__))

        last30 = dates.get_last_month(string=False)
        lastyear = dates.get_last_year(string=False)
        last3years = dates.get_last_3years(string=False)

        last30_subquery = Subquery(ds.LisPenden.objects.filter(bbl=OuterRef('bbl'), type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'], fileddate__gte=last30).values(
            'bbl').annotate(count=Count('bbl')).values('count'))

        lastyear_subquery = Subquery(ds.LisPenden.objects.filter(bbl=OuterRef(
            'bbl'), type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'], fileddate__gte=lastyear).values('bbl').annotate(count=Count('bbl')).values('count'))

        last3years_subquery = Subquery(ds.LisPenden.objects
                                       .filter(bbl=OuterRef('bbl'), type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'], fileddate__gte=last3years).values('bbl')
                                       .annotate(count=Count('bbl'))
                                       .values('count')
                                       )

        ds.PropertyAnnotation.objects.update(lispendens_last30=Coalesce(last30_subquery, 0), lispendens_lastyear=Coalesce(
            lastyear_subquery, 0), lispendens_last3years=Coalesce(last3years_subquery, 0), lispendens_lastupdated=datetime.now())

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_save, sender=LisPendenComment)
def annotate_property_on_save(sender, instance, created, **kwargs):
    if created == True:
        try:
            last30 = dates.get_last_month(string=False)
            lastyear = dates.get_last_year(string=False)
            last3years = dates.get_last_3years(string=False)

            annotation = ds.PropertyAnnotation.objects.get(bbl=instance.bbl)
            annotation.lispendens_last30 = Coalesce(annotation.bbl.acrisreallegal_set.filter(
                type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'], fileddate__gte=last30).count(), 0)

            annotation.lispendens_lastyear = Coalesce(annotation.bbl.acrisreallegal_set.filter(
                type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'], fileddate__gte=lastyear).count(), 0)

            annotation.lispendens_last3years = Coalesce(annotation.bbl.acrisreallegal_set.filter(
                type=ds.LisPenden.LISPENDEN_TYPES['foreclosure'], fileddate__gte=last3years).count(), 0)

            annotation.save()
        except Exception as e:
            print(e)
