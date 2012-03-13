from django.db import models
from django.db.models.query import Q
from django.utils.translation import ugettext as _

def mybulkcreate(objs):
    for obj in objs:
        obj.save()

class ClosureModel(models.Model):

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ClosureModel, self).__init__(*args, **kwargs)
        self._closure_old_parent_pk = self._closure_parent_pk

    #TODO: Move to metaclass
    @classmethod
    def create_closure_model(cls):
        model = type('%sClosure' % cls.__name__, (models.Model,), {
            'parent': models.ForeignKey(cls.__name__, related_name=cls._closure_parentref()),
            'child': models.ForeignKey(cls.__name__, related_name=cls._closure_childref()),
            'depth': models.IntegerField(),
            '__module__':   cls.__module__,
            '__unicode__': lambda self: "Closure from %s to %s" % (self.parent, self.child),
            'Meta': type('Meta', (object,), {
                'unique_together':  (("parent", "child"),)
            }),
        })
        setattr(cls, "_closure_model", model)
        return model

    @classmethod
    def rebuildtable(cls):
        cls._closure_model.objects.all().delete()
        bc = getattr(cls._closure_model.objects, "bulk_create", mybulkcreate)
        bc([cls._closure_model(parent_id=x['pk'], child_id=x['pk'], depth=0) for x in cls.objects.values("pk")])
        for node in cls.objects.all():
            node._closure_createlink()

    @classmethod
    def _closure_parentref(cls):
        return "%sclosure_children" % cls.__name__.lower()

    @classmethod
    def _closure_childref(cls):
        return "%sclosure_parents" % cls.__name__.lower()

    @property
    def _closure_parent_pk(self):
        parent = getattr(self, self.ClosureMeta.parent_attr)
        return parent.id if parent else None

    def _closure_deletelink(self, oldparentpk):
        self._closure_model.objects.filter(**{"parent__%s__child" % self._closure_parentref():oldparentpk,"child__%s__parent" % self._closure_childref():self.pk}).delete()
        #oldparentpks = [x['parent'] for x in self._closure_model.objects.filter(child__id=oldparentpk).values("parent")]
        #oldchildids = [x['child'] for x in self._closure_model.objects.filter(parent__id=self.id).values("child")]
        #self._closure_model.objects.filter(parent__id__in=oldparentpks,child__id__in=oldchildids).delete()

    def _closure_createlink(self):
        linkparents = self._closure_model.objects.filter(child__id=self._closure_parent_pk).values("parent", "depth")
        linkchildren = self._closure_model.objects.filter(parent__id=self.pk).values("child", "depth")
        newlinks = [self._closure_model(parent_id=p['parent'], child_id=c['child'], depth=p['depth']+c['depth']+1) for p in linkparents for c in linkchildren]
        bc = getattr(self._closure_model.objects, "bulk_create", mybulkcreate)
        bc(newlinks)

    def get_ancestors(self, include_self=False, depth=None):
        if self.is_root_node():
            if not include_self:
                return self.__class__.objects.none()
            else:
                # Filter on pk for efficiency.
                return self.__class__.objects.filter(pk=self.pk)

        qs = self.__class__.objects.filter(**{"%s__child" % self._closure_parentref():self.pk})
        if depth is not None:
            qs = qs.filter(**{"%s__depth" % self._closure_parentref():depth})
        if not include_self:
            qs = qs.exclude(pk=self.pk)
        return qs

    def get_descendants(self, include_self=False, depth=None):
        qs = self.__class__.objects.filter(**{"%s__parent" % self._closure_childref():self.pk})
        if depth is not None:
            qs = qs.filter(**{"%s__depth" % self._closure_childref():depth})
        if not include_self:
            qs = qs.exclude(pk=self.pk)
        return qs

    # Call like: blah.prepopulate(blah.get_descendants().select_related(stuff))
    def prepopulate(self, queryset):
        objs = list(queryset)
        hashobjs = dict([(x.pk,x) for x in objs] + [(self.pk, self)])
        for d in objs:
            if d._closure_parent_pk in hashobjs:
                p = hashobjs[d._closure_parent_pk]
                if not hasattr(p, "_cached_children"):
                    p._cached_children = []
                p._cached_children.append(d)

    def get_children(self):
        if hasattr(self, '_cached_children'):
            qs = self.__class__.objects.filter(pk__in=[n.pk for n in self._cached_children])
            qs._result_cache = self._cached_children
            return qs
        else:
            return self.get_descendants(include_self=False, depth=1)

    def get_root(self):
        if self.is_root_node():
            return self

        return self.get_ancestors().order_by("-%s__depth" % self._closure_parentref())[0]

    def is_child_node(self):
        return not self.is_root_node()

    def is_root_node(self):
        return self._closure_parent_pk is None

    def is_descendant_of(self, other, include_self=False):
        if include_self and other.pk == self.pk:
            return True

        return self._closure_model.objects.filter(parent=other,child=self).exists()

    def is_ancestor_of(self, other, include_self=False):
        if include_self and other.pk == self.pk:
            return True
        return other.is_descendant_of(self)

    def save(self, *args, **kwargs):
        create = not self.id
        val = super(ClosureModel, self).save(*args, **kwargs)
        if create:
            cm = self._closure_model(parent=self, child=self, depth=0)
            cm.save()
        if self._closure_old_parent_pk != self._closure_parent_pk:
            #Changed parents.
            if self._closure_old_parent_pk:
                self._closure_deletelink(self._closure_old_parent_pk)
            self._closure_createlink()
        self._closure_old_parent_pk = self._closure_parent_pk

        return val

    def delete(self, *args, **kwargs):
        self._closure_deletelink(self._closure_old_parent_pk)
        super(ClosureModel, self).delete(*args, **kwargs)
