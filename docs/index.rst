.. Django Closuretree documentation master file, created by
   sphinx-quickstart on Tue Jan 29 18:07:10 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-closuretree's documentation!
==============================================

**django-closuretree** is an implementation of a closure tree for tree-based
Django models. It aims to reduce the number of database hits required when
traversing complex tree-based relationships between models in your Django app.

Requirements
============

* Django 1.4+
* Sphinx (for documentation)

Basic Usage
===========

Inherit your models from ``closuretree.models.ClosureModel`` instead of ``django.db.models.Model``:

.. code-block:: python

    from django.db import models
    from closuretree.models import ClosureModel

    class MyModel(ClosureModel):
        parent = models.ForeignKey('self', related_name='children')
        name = models.CharField(max_length=32)

        def __unicode__(self):
            return '%s: %s" % (self.id, self.name)

**django-closuretree** will automatically use the field named ``parent`` as the
relationship. This can be manually overriden:

.. code-block:: python

    from django.db import models
    from closuretree.models import ClosureModel
    
    class MyModel(ClosureModel):
        parent_rel = models.ForeignKey('self', related_name='children')
        name = models.CharField(max_length=32)

        class ClosureMeta(object):
            parent_attr = 'parent_rel'

        def __unicode__(self):
            return '%s: %s' % (self.id, self.name)

Perhaps the most useful methods provided by ``closuretree.models.ClosureModel`` are
the following:

.. code-block:: python

    >> my_model = MyModel.objects.get(pk=10)
    >> my_model.get_ancestors()
    [<MyModel: 1: Foo>, <MyModel: 2: Bar>, <MyModel: 3: Fish>]
    >> my_model.get_descendants()
    [<MyModel: 11: Bob>, <MyModel: 12: Alice>]
    >> my_model.get_descendants(depth=1)
    [<MyModel: 11: Bob>]
    >> my_model.get_root()
    <MyModel: 1: Foo>
    >> my_model.is_ancestor_of(MyModel.objects.get(name='Alice'))
    True
    >> my_model.is_descendant_of(MyModel.objects.get(name='Bar'))
    True

Read the :doc:`closuretree` model documentation for more methods.

Adding to existing models
=========================

If you add **django-closuretree** to existing models, you'll need to build the closure table for the pre-existing data:

.. code-block:: python

    MyModel.rebuildtable()

Indirect relations
==================

If your model is linked to itself via an indirect relationship (for example, ModelA -> ModelB -> ModelC -> ModelA), then you'll need to define a parent property that traverses this relationship, and set a sentinel attribute as the foriegn key to ModelB:

.. code-block:: python

    class ModelA(ClosureModel):
        model_b = models.ForeignKey(ModelB)

        @property
        def parent(self):
            return self.model_b.model_c.model_a

        class ClosureMeta:
            sentinel_attr = 'model_b'
           
Closuretree will watch the sentinel attribute for changes, and use the value of the parent property when rebuilding the tree.

API Documentation
=================

.. toctree::
   :maxdepth: 2

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

