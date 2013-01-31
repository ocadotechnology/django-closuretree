"""Tests for closuretree"""

# This is kinda tricky...
# pylint: disable=C0103
# pylint: disable=E1101
# pylint: disable=E0602
# pylint: disable=R0903
# pylint: disable=R0904
# pylint: disable=
# pylint: disable=

from django.test import TestCase
from django.db import models
from closuretree.models import ClosureModel

class TC(ClosureModel):
    """A test model."""
    parent2 = models.ForeignKey(
        "self",
        related_name="children",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=32)
    blah = models.ForeignKey("Blah", related_name="tcs", null=True, blank=True)

    class ClosureMeta(object):
        """Closure options."""
        parent_attr = "parent2"

    def __unicode__(self):
        return "%s: %s" % (self.id, self.name)

class Blah(models.Model):
    """A test model for foreign keys"""
    thing = models.CharField(max_length=32)

class TCSUB(TC):
    """Testing closure subclasses."""
    extrafield = models.IntegerField()

class TCSUB2(TCSUB):
    """Testing closure subclasses."""
    ef = models.IntegerField()

class BaseTesting(TestCase):
    """Providing details for testing."""

    def setUp(self):
        self.a = TC.objects.create(name="a")
        self.b = TC.objects.create(name="b")
        self.c = TC.objects.create(name="c")
        self.d = TC.objects.create(name="d")

    def test_adding(self):
        """
        Tests that adding a new parent relationship creates closures
        """
        self.failUnlessEqual(TCClosure.objects.count(), 4)
        self.b.parent2 = self.a
        self.b.save()
        self.failUnlessEqual(TCClosure.objects.count(), 5)
        self.c.parent2 = self.b
        self.c.save()
        self.d.parent2 = self.c
        self.d.save()
        self.failUnlessEqual(TCClosure.objects.count(), 10)

    def test_deletion(self):
        """
            Tests that deleting a relationship removes the closure entries.
        """
        self.failUnlessEqual(TCClosure.objects.count(), 4)
        self.b.parent2 = self.a
        self.b.save()
        self.failUnlessEqual(TCClosure.objects.count(), 5)
        self.b.parent2 = None
        self.b.save()
        self.failUnlessEqual(TCClosure.objects.count(), 4)

class AncestorTesting(TestCase):
    """Testing things to do with ancestors."""

    def setUp(self):
        self.a = TC.objects.create(name="a")
        self.b = TC.objects.create(name="b")
        self.c = TC.objects.create(name="c")
        self.b.parent2 = self.a
        self.b.save()
        self.c.parent2 = self.b
        self.c.save()

    def test_ancestors(self):
        """Testing the ancestors method."""
        self.failUnlessEqual(list(self.a.get_ancestors()), [])
        self.failUnlessEqual(list(self.b.get_ancestors()), [self.a])
        self.failUnlessEqual(
            list(self.a.get_ancestors(include_self=True)),
            [self.a]
        )
        self.failUnlessEqual(
            list(self.c.get_ancestors(include_self=True)),
            [self.c, self.b, self.a]
        )

    def test_descendants(self):
        """Testing the descendants method."""
        self.failUnlessEqual(list(self.c.get_descendants()), [])
        self.failUnlessEqual(list(self.b.get_descendants()), [self.c])
        self.failUnlessEqual(
            list(self.a.get_descendants(include_self=True)),
            [self.a, self.b, self.c]
        )
        self.failUnlessEqual(
            list(self.c.get_descendants(include_self=True)),
            [self.c]
        )

    def test_children(self):
        """Testing the children method."""
        self.failUnlessEqual(list(self.c.get_children()), [])
        self.failUnlessEqual(list(self.b.get_children()), [self.c])
