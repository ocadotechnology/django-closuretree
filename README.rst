******************
django-closuretree
******************


.. image:: https://travis-ci.org/ocadotechnology/django-closuretree.svg
   :target: https://travis-ci.org/ocadotechnology/django-closuretree
   :alt: Build Status
.. image:: https://landscape.io/github/ocadotechnology/django-closuretree/master/landscape.svg?style=flat
   :target: https://landscape.io/github/ocadotechnology/django-closuretree/master
   :alt: Code Health Badge
.. image:: https://readthedocs.org/projects/django-closuretree/badge/?version=latest
   :target: http://django-closuretree.readthedocs.org/en/latest/
   :alt: Documentation Status
.. image:: https://coveralls.io/repos/ocadotechnology/django-closuretree/badge.svg
   :target: https://coveralls.io/r/ocadotechnology/django-closuretree
   :alt: Test Coverage
.. image:: https://pypip.in/v/django-closuretree/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/django-closuretree/
   :alt: Version Badge
.. image:: https://pypip.in/license/django-closuretree/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/django-closuretree/
   :alt: License Badge


``django-closuretree`` is an implementation of the `closure tree <http://homepages.inf.ed.ac.uk/libkin/papers/tc-sql.pdf>`_ technique for `Django <https://djangoproject.com>`_ applications designed to provide efficient querying of `tree-based structures <http://en.wikipedia.org/wiki/Tree_%28data_structure%29>`_ in a relational database. Its goal is to reduce the number of queries required when querying the children or parents of a given object.

Given the following model:

.. code-block:: python

    class Node(models.Model):
        name = models.CharField(max_length=24)
        parent = models.ForeignKey('self', related_name='children')

The children of each model can be queried with:

.. code-block:: python

    Node.objects.get(name='A').children.all()

However, for recursive lookups, this results in a large number of queries. Instead, ``django-closuretree`` allows you to extract them all in one go:

.. code-block:: python

    from closuretree.models import ClosureModel

    class Node(ClosureModel):
        name = models.CharField(max_length=24)
        parent = models.ForeignKey('self', related_name='children', null=True)

    a = Node.objects.create(name='A')
    Node.objects.create(name='B', parent=a)

    Node.objects.get(name='A').get_descendants()

A single query will obtain all the descendants.

===========
Quick Start
===========

* Install ``django-closuretree`` with ``pip install django-closuretree``.
* Inherit your models from ``closuretree.models.ClosureModel`` instead of ``django.db.models.Model``.

That's it. You can now use ``get_descendants()`` and ``get_ancestors()`` on a model instance.

If you're adding this to an existing application that already has data in the database, you'll need to run the ``rebuildtable()`` method of each model before the closure tree will be populated with the existing data:

.. code-block:: python

    Node.rebuildtable()

============
Contributing
============

To contribute, fork the repo, do your work, and issue a pull request. We ask that contributors adhere to `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ standards, and include full tests for all their code.
