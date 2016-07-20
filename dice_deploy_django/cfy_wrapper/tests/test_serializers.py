from rest_framework.serializers import ValidationError

from .base import BaseTest

import datetime
import mock
import uuid

from cfy_wrapper.serializers import (
    BlueprintSerializer,
    ContainerSerializer,
    InputSerializer,
)

from cfy_wrapper.models import Input


class BlueprintSerializerTest(BaseTest):

    def test_valid_serialization(self):
        id = uuid.uuid4()
        b = mock.MagicMock(id=id, state_name="test", outputs={"k": "v"},
                           modified_date=datetime.datetime(2015, 10, 3),
                           in_error=False)
        d = BlueprintSerializer(b).data
        self.assertEqual({
            "id": str(id),
            "state_name": "test",
            "modified_date": "2015-10-03T00:00:00",
            "outputs": {"k": "v"},
            "in_error": False,
        }, d)

    def test_prevent_saving(self):
        id = uuid.uuid4()
        data = {
            "id": str(id),
            "state_name": "test",
            "modified_date": "2015-10-03T00:00:00",
            "outputs": {"test": "dict"},
            "in_error": True,
        }
        s = BlueprintSerializer(data=data)
        s.is_valid()
        self.assertTrue(s.is_valid(raise_exception=True))
        with self.assertRaises(Exception):
            s.save()


class ContainerSerializerTest(BaseTest):

    def test_valid_serialization(self):
        b_id = uuid.uuid4()
        c_id = uuid.uuid4()
        b = mock.MagicMock(id=b_id, state_name="test", outputs={"k": "v"},
                           modified_date=datetime.datetime(2015, 10, 3),
                           in_error=True)
        c = mock.MagicMock(id=c_id, description="desc", blueprint=b,
                           modified_date=datetime.datetime(2016, 11, 2))
        d = ContainerSerializer(c).data

        # Blueprint field is at this stage a OrderedDict, which would break
        # comparison with ordinary dict.
        d["blueprint"] = dict(d["blueprint"])

        self.assertEqual({
            "id": str(c_id),
            "description": "desc",
            "modified_date": "2016-11-02T00:00:00",
            "blueprint": {
                "id": str(b_id),
                "state_name": "test",
                "modified_date": "2015-10-03T00:00:00",
                "outputs": {"k": "v"},
                "in_error": True,
            }
        }, d)

    def test_prevent_saving(self):
        id = uuid.uuid4()
        data = {
            "id": str(id),
            "description": "desc",
            "modified_date": "2016-11-02T00:00:00",
            "blueprint": {
                "id": str(id),
                "state_name": "test",
                "modified_date": "2015-10-03T00:00:00",
                "outputs": {"k": "v"},
            }
        }
        s = ContainerSerializer(data=data)
        self.assertTrue(s.is_valid(raise_exception=True))
        with self.assertRaises(Exception):
            s.save()


class InputSerializerTest(BaseTest):

    def test_valid_serialization(self):
        data = {
            "key": "sample-key",
            "value": "sample-value",
            "description": "sample-desc",
        }
        i = mock.MagicMock(**data)
        d = InputSerializer(i).data
        self.assertEqual(d, data)

    def test_valid_save(self):
        data = {
            "key": "sample-key",
            "value": "sample-value",
            "description": "sample-desc",
        }
        s = InputSerializer(data=data)
        self.assertTrue(s.is_valid(raise_exception=True))
        s.save()
        i = Input.objects.get(key=data["key"])
        for k, v in data.items():
            self.assertEqual(getattr(i, k), v)

    def test_prevent_duplicate_key(self):
        data = {
            "key": "sample-key",
            "value": "sample-value",
            "description": "sample-desc",
        }
        Input.objects.create(**data)
        s = InputSerializer(data=data)
        with self.assertRaises(ValidationError):
            s.is_valid(raise_exception=True)

    def test_updating(self):
        orig = {
            "key": "sample-key",
            "value": "sample-value",
            "description": "sample-desc",
        }
        data = {
            "key": "sample-key",
            "value": "new-value",
            "description": "new-desc",
        }
        i = Input.objects.create(**orig)
        s = InputSerializer(i, data=data)
        self.assertTrue(s.is_valid(raise_exception=True))
        s.save()
        i.refresh_from_db()
        for k, v in data.items():
            self.assertEqual(getattr(i, k), v)