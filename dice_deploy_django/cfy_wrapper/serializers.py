from rest_framework import serializers

from .models import Blueprint, Container, Input


class BlueprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blueprint
        fields = ("id", "state_name", "modified_date", "outputs", "in_error")

    outputs = serializers.JSONField()

    def save(*args, **kwargs):
        raise RuntimeError("Blueprint saving is not supported")

    def update(*args, **kwargs):
        raise RuntimeError("Blueprint updating is not supported")


class ContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Container
        fields = ("id", "description", "blueprint", "modified_date")
        read_only_fields = ("blueprint",)

    blueprint = BlueprintSerializer()


class InputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Input
        fields = ("key", "value", "description")
