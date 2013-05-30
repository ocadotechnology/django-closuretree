.. Django Closuretree documentation master file, created by
   sphinx-quickstart on Tue Jan 29 18:07:10 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django Closuretree's documentation!
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

To take advantage of **django-closuretree**, instead of inheriting your models from
``django.db.models.Model``, inherit from ``closuretree.models.ClosureModel``:

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

API Documentation
-----------------

.. toctree::
   :maxdepth: 2

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

