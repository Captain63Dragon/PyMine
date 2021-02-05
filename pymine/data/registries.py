import json
import os

from pymine.util.immutable import make_immutable
from pymine.types.registry import Registry

__all__ = ("ITEM_REGISTRY", "PARTICLE_REGISTRY", "FLUID_REGISTRY", "BLOCK_REGISTRY", "ENTITY_REGISTRY", "BLOCK_DATA")

with open(os.path.join("pymine", "data", "registries.json"), "r") as registry:  # generated from server jar
    REGISTRY_DATA = make_immutable(json.load(registry))

ITEM_REGISTRY = Registry({k: v["protocol_id"] for k, v in REGISTRY_DATA["minecraft:item"]["entries"].items()})
PARTICLE_REGISTRY = Registry({k: v["protocol_id"] for k, v in REGISTRY_DATA["minecraft:particle_type"]["entries"].items()})
FLUID_REGISTRY = Registry({k: v["protocol_id"] for k, v in REGISTRY_DATA["minecraft:fluid"]["entries"].items()})
BLOCK_REGISTRY = Registry({k: v["protocol_id"] for k, v in REGISTRY_DATA["minecraft:block"]["entries"].items()})
ENTITY_REGISTRY = Registry({k: v["protocol_id"] for k, v in REGISTRY_DATA["minecraft:entity_type"]["entries"].items()})

with open(os.path.join("pymine", "data", "blocks.json"), "r") as block_data:
    block_state_data = make_immutable(json.load(block_data))

BLOCK_STATE = Registry(block_state_data, {state_val["id"]: {"name": k, "properties": state_val["properties"]} for k, state_val in block_state_data.items()})
