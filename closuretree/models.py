from django.db import models
from django.db.models.query import Q
from django.utils.translation import ugettext as _

def mybulkcreate(objs):
    for obj in objs:
        obj.save()

class ClosureModel(models.Model):
    """
    Base class for tree models.
    """

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
            '__module__':   cls.__module__,
            '__unicode__': lambda self: "Closure from %s to %s" % (self.parent, self.child),
        })
        setattr(cls, "_closure_model", model)
        return model

    @classmethod
    def rebuildtable(cls):
        cls._closure_model.objects.all().delete()
        bc = getattr(cls._closure_model.objects, "bulk_create", mybulkcreate)
        bc([cls._closure_model(parent_id=x['pk'], child_id=x['pk']) for x in cls.objects.values("pk")])
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
        field = self._meta.get_field(self.ClosureMeta.parent_attr)
        return field.value_from_object(self)

    def _closure_deletelink(self, oldparentpk):
        self._closure_model.objects.filter({"parent__%s__child" % self._closure_parentref():oldparentpk,"child__%s__parent" % self._closure_childref():self.pk}).delete()
        #oldparentpks = [x['parent'] for x in self._closure_model.objects.filter(child__id=oldparentpk).values("parent")]
        #oldchildids = [x['child'] for x in self._closure_model.objects.filter(parent__id=self.id).values("child")]
        #self._closure_model.objects.filter(parent__id__in=oldparentpks,child__id__in=oldchildids).delete()

    def _closure_createlink(self):
        linkparents = [x['parent'] for x in self._closure_model.objects.filter(child__id=self._closure_parent_pk).values("parent")]
        linkchildren = [x['child'] for x in self._closure_model.objects.filter(parent__id=self.pk).values("child")]
        newlinks = [self._closure_model(parent_id=p, child_id=c) for p in linkparents for c in linkchildren]
        bc = getattr(self._closure_model.objects, "bulk_create", mybulkcreate)
        bc(newlinks)

    def get_ancestors(self, include_self=False):
        if self.is_root_node():
            if not include_self:
                return self.__class__.objects.none()
            else:
                # Filter on pk for efficiency.
                return self.__class__.objects.filter(pk=self.pk)

        qs = self.__class__.objects.filter({"__child" % self._closure_parentref():self.pk})
        if not include_self:
            qs = qs.exclude(pk=self.pk)
        return qs

    def get_descendants(self, include_self=False):
        qs = self.__class__.objects.


    def get_root(self):
        """
        Returns the root node of this model instance's tree.
        """
        if self.is_root_node() and type(self) == self._tree_manager.tree_model:
            return self

        return self._tree_manager._mptt_filter(
            tree_id=self._mpttfield('tree_id'),
            parent__isnull=True
        ).get()

    def get_siblings(self, include_self=False):
        """
        Creates a ``QuerySet`` containing siblings of this model
        instance. Root nodes are considered to be siblings of other root
        nodes.

        If ``include_self`` is ``True``, the ``QuerySet`` will also
        include this model instance.
        """
        if self.is_root_node():
            queryset = self._tree_manager._mptt_filter(parent__isnull=True)
        else:
            parent_id = getattr(self, '%s_id' % self._mptt_meta.parent_attr)
            queryset = self._tree_manager._mptt_filter(parent__id=parent_id)
        if not include_self:
            queryset = queryset.exclude(pk=self.pk)
        return queryset

    def is_child_node(self):
        """
        Returns ``True`` if this model instance is a child node, ``False``
        otherwise.
        """
        return not self.is_root_node()

    def is_leaf_node(self):
        """
        Returns ``True`` if this model instance is a leaf node (it has no
        children), ``False`` otherwise.
        """
        return not self.get_descendant_count()

    def is_root_node(self):
        """
        Returns ``True`` if this model instance is a root node,
        ``False`` otherwise.
        """
        return self._closure_parent_pk is None

    def is_descendant_of(self, other, include_self=False):
        """
        Returns ``True`` if this model is a descendant of the given node,
        ``False`` otherwise.
        If include_self is True, also returns True if the two nodes are the same node.
        """
        opts = self._mptt_meta

        if include_self and other.pk == self.pk:
            return True

        if getattr(self, opts.tree_id_attr) != getattr(other, opts.tree_id_attr):
            return False
        else:
            left = getattr(self, opts.left_attr)
            right = getattr(self, opts.right_attr)

            return left > getattr(other, opts.left_attr) and right < getattr(other, opts.right_attr)

    def is_ancestor_of(self, other, include_self=False):
        """
        Returns ``True`` if this model is an ancestor of the given node,
        ``False`` otherwise.
        If include_self is True, also returns True if the two nodes are the same node.
        """
        if include_self and other.pk == self.pk:
            return True
        return other.is_descendant_of(self)

    def save(self, *args, **kwargs):
        create = not self.id
        val = super(ClosureModel, self).save(*args, **kwargs)
        if create:
            cm = self._closure_model(parent=self, child=self)
            cm.save()
        if self._closure_old_parent_pk != self.pk:
            #Changed parents.
            if self._closure_old_parent_pk:
                self._closure_deletelink(self._closure_old_parent_pk)
            self._closure_createlink()
        self._closure_old_parent_pk = self._closure_parent_pk

        return val

    def delete(self, *args, **kwargs):
        tree_width = (self._mpttfield('right') -
                      self._mpttfield('left') + 1)
        target_right = self._mpttfield('right')
        tree_id = self._mpttfield('tree_id')
        self._tree_manager._close_gap(tree_width, target_right, tree_id)
        super(MPTTModel, self).delete(*args, **kwargs)
