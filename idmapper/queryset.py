from django.db.models.query import QuerySet


class SharedMemoryQuerySet(QuerySet):
    def get(self, **kwargs):
        instance = None
        pk_attr = self.model._meta.pk.attname

        pk_interceptions = (
            'pk',
            'pk__exact',
            pk_attr,
            '%s__exact' % pk_attr
        )

        # This is an exact lookup for the pk only -> kwargs.values()[0] is the pk
        if len(kwargs) == 1 and kwargs.keys()[0] in pk_interceptions:
            instance = self.model.get_cached_instance(kwargs.values()[0])

        where_children = self.query.where.children

        if len(where_children) == 1:
            lookup = where_children[0]

            if lookup.lhs.target.name in ('pk', pk_attr) and lookup.lookup_name == 'exact':
                instance = self.model.get_cached_instance(lookup.rhs)

        # The cache missed or was not applicable, hit the database!
        if instance is None:
            instance = super(SharedMemoryQuerySet, self).get(**kwargs)

        return instance
