"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from tclosure.models import TC, TCClosure

class BaseTesting(TestCase):

    def setUp(self):
        self.a = TC.objects.create(name="a")
        self.b = TC.objects.create(name="b")
        self.c = TC.objects.create(name="c")
        self.d = TC.objects.create(name="d")

    def test_adding(self):
        """
        Tests that adding a new parent relationship creates closures
        """
        self.failUnlessEqual(TCClosure.objects.count(), 17)
        self.b.parent2 = self.a
        self.b.save()
        self.failUnlessEqual(TCClosure.objects.count(), 18)
        self.c.parent2 = self.b
        self.c.save()
        self.d.parent2 = self.c
        self.d.save()
        self.failUnlessEqual(TCClosure.objects.count(), 23)

    def test_deletion(self):
        self.failUnlessEqual(TCClosure.objects.count(), 17)
        self.b.parent2 = self.a
        self.b.save()
        self.failUnlessEqual(TCClosure.objects.count(), 18)
        self.b.parent2 = None
        self.b.save()
        self.failUnlessEqual(TCClosure.objects.count(), 17)

class AncestorTesting(TestCase):

    def setUp(self):
        self.a = TC.objects.create(name="a")
        self.b = TC.objects.create(name="b")
        self.c = TC.objects.create(name="c")
        self.b.parent2 = self.a
        self.b.save()
        self.c.parent2 = self.b
        self.c.save()

    def test_ancestors(self):
        self.failUnlessEqual(list(self.a.get_ancestors()), [])
        self.failUnlessEqual(list(self.b.get_ancestors()), [self.a])
        self.failUnlessEqual(list(self.a.get_ancestors(include_self=True)), [self.a])
        self.failUnlessEqual(list(self.c.get_ancestors(include_self=True)), [self.c, self.b, self.a])

    def test_descendants(self):
        self.failUnlessEqual(list(self.c.get_descendants()), [])
        self.failUnlessEqual(list(self.b.get_descendants()), [self.c])
        self.failUnlessEqual(list(self.a.get_descendants(include_self=True)), [self.a, self.b, self.c])
        self.failUnlessEqual(list(self.c.get_descendants(include_self=True)), [self.c])

    def test_children(self):
        self.failUnlessEqual(list(self.c.get_children()), [])
        self.failUnlessEqual(list(self.b.get_children()), [self.c])
