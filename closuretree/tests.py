# Copyright 2015 Ocado Innovation Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for closuretree"""

# This is kinda tricky...
# pylint: disable=C0103
# pylint: disable=E1101
# pylint: disable=E0602
# pylint: disable=R0903
# pylint: disable=R0904
# pylint: disable=
# pylint: disable=

from django import VERSION
from django.test import TestCase
from django.db import models
from closuretree.models import ClosureModel
import uuid

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
        return "%s: %s" % (self.pk, self.name)

class Blah(models.Model):
    """A test model for foreign keys"""
    thing = models.CharField(max_length=32)

class TCSUB(TC):
    """Testing closure subclasses."""
    extrafield = models.IntegerField()

class TCSUB2(TCSUB):
    """Testing closure subclasses."""
    ef = models.IntegerField()

class BaseTestCase(TestCase):
    """Providing details for testing."""

    normal_model = TC
    closure_model = TCClosure

    def setUp(self):
        self.a = self.normal_model.objects.create(name="a")
        self.b = self.normal_model.objects.create(name="b")
        self.c = self.normal_model.objects.create(name="c")
        self.d = self.normal_model.objects.create(name="d")

        # We cheat here, we don't care about the __unicode__ method,
        # It's only useful when we're working out why the tests fail.
        self.a.__unicode__()

    def test_unicode(self):
        """Test unicoding of the closures works."""
        # No, it's a method for unittest!
        # pylint: disable=R0201

        for obj in self.closure_model.objects.all():
            obj.__unicode__()

    def test_adding(self):
        """
        Tests that adding a new parent relationship creates closures
        """
        self.failUnlessEqual(self.closure_model.objects.count(), 4)
        self.b.parent2 = self.a
        self.b.save()
        self.failUnlessEqual(self.closure_model.objects.count(), 5)
        self.c.parent2 = self.b
        self.c.save()
        # Test double save
        self.c.save()
        self.d.parent2 = self.c
        self.d.save()
        self.failUnlessEqual(self.closure_model.objects.count(), 10)

    def test_deletion(self):
        """
            Tests that deleting a relationship removes the closure entries.
        """
        self.failUnlessEqual(self.closure_model.objects.count(), 4)
        self.b.parent2 = self.a
        self.b.save()
        self.failUnlessEqual(self.closure_model.objects.count(), 5)
        self.b.parent2 = None
        self.b.save()
        self.failUnlessEqual(self.closure_model.objects.count(), 4)
        self.b.parent2 = self.a
        self.b.save()
        self.c.parent2 = self.b
        self.c.save()
        self.failUnlessEqual(self.closure_model.objects.count(), 7)
        self.b.delete()
        self.failUnlessEqual(self.closure_model.objects.count(), 2)


if VERSION >= (1, 8):
    class UUIDTC(ClosureModel):
        '''Testing support for models with a UUID primary key. See #30'''
        primary_key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        parent2 = models.ForeignKey(
            "self",
            related_name="children",
            null=True,
            blank=True,
        )
        name = models.CharField(max_length=32)

        class ClosureMeta(object):
            """Closure options."""
            parent_attr = "parent2"

        def __unicode__(self):
            return "%s: %s" % (self.pk, self.name)


    class UUIDTestCase(BaseTestCase):
        '''Testing UUID models. See #30'''
        normal_model = UUIDTC
        closure_model = UUIDTCClosure


class AncestorTestCase(TestCase):
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
        self.failUnlessEqual(
            list(self.c.get_ancestors(include_self=True, depth=1)),
            [self.c, self.b]
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

class RebuildTestCase(TestCase):
    """Test rebuilding the tree"""

    def setUp(self):
        self.a = TC.objects.create(name="a")
        self.b = TC.objects.create(name="b")
        self.b.parent2 = self.a
        self.b.save()
        self.c = TC.objects.create(name="c")
        self.c.parent2 = self.b
        self.c.save()
        self.d = TC.objects.create(name="d")
        self.d.parent2 = self.a
        self.d.save()

    def test_rebuild_from_full(self):
        """Test a rebuild when the tree is correct."""

        self.failUnlessEqual(TCClosure.objects.count(), 8)
        TC.rebuildtable()
        self.failUnlessEqual(TCClosure.objects.count(), 8)

    def test_rebuild_from_empty(self):
        """Test a rebuild when the tree is empty."""

        TCClosure.objects.all().delete()
        TC.rebuildtable()
        self.failUnlessEqual(TCClosure.objects.count(), 8)

    def test_rebuild_from_partial(self):
        """Test a rebuild when the tree is partially empty."""

        TCClosure.objects.get(parent__name='a', child__name='a').delete()
        TCClosure.objects.get(parent__name='a', child__name='c').delete()
        self.failUnlessEqual(TCClosure.objects.count(), 6)
        TC.rebuildtable()
        self.failUnlessEqual(TCClosure.objects.count(), 8)

class InitialClosureTestCase(TestCase):
    """Tests for when things are created with a parent."""

    def test_creating_with_parent(self):
        """Make sure closures are created when making objects."""
        a = TC.objects.create(name="a")
        self.failUnlessEqual(TCClosure.objects.count(), 1)
        b = TC.objects.create(name="b", parent2=a)
        self.failUnlessEqual(TCClosure.objects.count(), 3)
        TC.objects.create(name="c", parent2=b)
        self.failUnlessEqual(TCClosure.objects.count(), 6)

class IsTestCase(TestCase):
    """Test some useful methods."""

    def setUp(self):
        self.a = TC.objects.create(name="a")
        self.b = TC.objects.create(name="b", parent2=self.a)
        self.c = TC.objects.create(name="c", parent2=self.b)
        self.d = TC.objects.create(name="d", parent2=self.c)
        self.e = TC.objects.create(name="e", parent2=self.b)
        self.f = TC.objects.create(name="f", parent2=self.e)

    def test_ancestor_of(self):
        """Test is_ancestor_of method."""
        self.assertEqual(self.a.is_ancestor_of(self.c), True)
        self.assertEqual(self.a.is_ancestor_of(self.d), True)
        self.assertEqual(self.a.is_ancestor_of(self.e), True)
        self.assertEqual(self.d.is_ancestor_of(self.b), False)
        self.assertEqual(
            self.d.is_ancestor_of(self.b, include_self=True),
            False
        )
        self.assertEqual(self.f.is_ancestor_of(self.f), False)
        self.assertEqual(
            self.f.is_ancestor_of(self.f, include_self=False),
            False
        )
        self.assertEqual(self.f.is_ancestor_of(self.f, include_self=True), True)

    def test_descendant_of(self):
        """Test id_descendant_of method."""
        self.assertEqual(self.a.is_descendant_of(self.a), False)
        self.assertEqual(self.f.is_descendant_of(self.f), False)
        self.assertEqual(
            self.a.is_descendant_of(self.a, include_self=False), False
        )
        self.assertEqual(
            self.a.is_descendant_of(self.a, include_self=True), True
        )
        self.assertEqual(self.a.is_descendant_of(self.c), False)
        self.assertEqual(self.c.is_descendant_of(self.a), True)

    def test_get_root(self):
        """Test get_root method"""
        self.assertEqual(self.a.get_root(), self.a)
        self.assertEqual(self.b.get_root(), self.a)
        self.assertEqual(self.f.get_root(), self.a)

    def test_child_node(self):
        """Test is_child_node method"""
        self.assertEqual(self.a.is_child_node(), False)
        self.assertEqual(self.b.is_child_node(), True)
        self.assertEqual(self.f.is_child_node(), True)

class PrepopulateTestCase(TestCase):
    """Test prepopulating."""

    def setUp(self):
        self.a = TC.objects.create(name="a")
        self.b = TC.objects.create(name="b", parent2=self.a)
        self.c = TC.objects.create(name="c", parent2=self.b)
        self.d = TC.objects.create(name="d", parent2=self.c)
        self.e = TC.objects.create(name="e", parent2=self.b)
        self.f = TC.objects.create(name="f", parent2=self.e)

    def test_prepopulate(self):
        """Test prepopulating"""
        with self.assertNumQueries(6):
            children = []
            for node in self.a.get_descendants():
                children.extend(list(node.get_children()))
            self.assertEqual(len(children), 4)
        with self.assertNumQueries(1):
            children = []
            queryset = self.a.get_descendants()
            self.a.prepopulate(queryset)
            for node in queryset:
                children.extend(list(node.get_children()))
            self.assertEqual(len(children), 4)

    def test_prepopulate_not_root(self):
        """Test prepopulating when we're not the root"""
        with self.assertNumQueries(5):
            children = []
            for node in self.b.get_descendants():
                children.extend(list(node.get_children()))
            self.assertEqual(len(children), 2)
        with self.assertNumQueries(1):
            children = []
            queryset = self.b.get_descendants()
            self.b.prepopulate(queryset)
            for node in queryset:
                children.extend(list(node.get_children()))
            self.assertEqual(len(children), 2)

class SentinelModel(ClosureModel):
    """A model using a sentinel attribute."""
    location = models.ForeignKey(
        "IntermediateModel",
        null=True,
        blank=True
    )

    @property
    def parent(self):
        """Return the object's parent."""
        if self.location:
            return self.location.real_parent

    class ClosureMeta(object):
        """Closure options."""
        sentinel_attr = "location"
        parent_attr = "parent"

class IntermediateModel(models.Model):
    """The intermediate model between the sentinel model
        and its parent (itself).
    """
    real_parent = models.ForeignKey(
        'SentinelModel',
        null=True,
        blank=True,
    )

class SentinelAttributeTestCase(TestCase):
    """Test functionality of the sentinel attribute."""

    def setUp(self):
        self.a = SentinelModel.objects.create()
        self.b = SentinelModel.objects.create()
        self.c = SentinelModel.objects.create()
        self.d = SentinelModel.objects.create()
        self.l1 = IntermediateModel.objects.create(real_parent=self.a)
        self.l2 = IntermediateModel.objects.create(real_parent=self.b)
        self.l3 = IntermediateModel.objects.create(real_parent=self.c)

    def test_closure_creation(self):
        '''Test creation of closures in the sentinel case'''

        self.failUnlessEqual(SentinelModelClosure.objects.count(), 4)

        self.b.location = self.l1
        self.b.save()
        self.failUnlessEqual(self.b.parent, self.a)
        self.c.location = self.l2
        self.c.save()

        self.failUnlessEqual(SentinelModelClosure.objects.count(), 7)

    def test_num_queries(self):
        '''Test that we don't need to access the objects until we make a change.'''
        self.b.location = self.l1
        self.b.save()
        self.c.location = self.l1
        self.c.save()

        with self.assertNumQueries(1):
            x = SentinelModel.objects.get(pk=self.b.pk)
            x.location = self.l1

        with self.assertNumQueries(1):
            x = SentinelModel.objects.select_related('location__real_parent').get(pk=self.b.pk)
            x.location = self.l2


class TCNoMeta(ClosureModel):
    """A test model without a ClosureMeta."""
    parent = models.ForeignKey(
        "self",
        related_name="children",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=32)

class NoMetaTestCase(TestCase):
    '''Testing models without a ClosureMeta.'''

    def test_basic(self):
        """
        Basic test that you don't need the ClosureMeta class.
        """
        a = TCNoMeta.objects.create(name='a')
        b = TCNoMeta.objects.create(name='b', parent=a)
        c = TCNoMeta.objects.create(name='c', parent=b)
        self.failUnlessEqual(a.get_descendants().count(), 2)
        self.failUnlessEqual(c.get_ancestors().count(), 2)
