from typing import Any, TypeAlias

JSON: TypeAlias = dict[str, Any]


class Model:
    """Базовая модель-обёртка над словарём payload"""
    def __init__(self, payload: JSON):
        if not isinstance(payload, dict):
            raise TypeError("Payload must be a dict-like JSON object")
        self.payload = payload


class Field:
    """Дескриптор поля модели"""
    def __init__(self, path: str):
        if not path or not isinstance(path, str):
            raise ValueError("Path must be a non-empty string")
        self.path = path
        self._attr_name: str | None = None

    def __set_name__(self, owner, name: str) -> None:
        self._attr_name = name

    def __get__(self, instance: Model | None, owner=None):
        if instance is None:
            return self
        return self._get_from_payload(instance.payload)

    def __set__(self, instance: Model, value: Any) -> None:
        self._set_to_payload(instance.payload, value)

    def __delete__(self, instance: Model) -> None:
        self._delete_from_payload(instance.payload)

    def _keys(self) -> list[str]:
        return self.path.split(".")

    def _get_from_payload(self, payload: JSON) -> Any:
        node: Any = payload
        for key in self._keys():
            if not isinstance(node, dict) or key not in node:
                return None
            node = node[key]
        return node

    def _set_to_payload(self, payload: JSON, value: Any) -> None:
        keys = self._keys()
        node: Any = payload
        for key in keys[:-1]:
            if not isinstance(node, dict):
                break
            if key not in node or not isinstance(node[key], dict):
                node[key] = {}
            node = node[key]
        if isinstance(node, dict):
            node[keys[-1]] = value

    def _delete_from_payload(self, payload: JSON) -> None:
        keys = self._keys()
        node: Any = payload
        for key in keys[:-1]:
            if not isinstance(node, dict) or key not in node:
                return
            node = node[key]
        if isinstance(node, dict):
            node.pop(keys[-1], None)



def main():
    class Movie(Model):
        name = Field("name")
        rating = Field("rating.main")
        modificator = Field("rating.modificator")
    
    payload_minecraft = {
        "name": "Minecraft Movie",
        "rating": {
            "main": 9,
            "modificator": +1
        }
    }

    minecraft = Movie(payload_minecraft)

    print(f"Полный рейтинг {minecraft.name}: {minecraft.rating + minecraft.modificator} / 10")



if __name__ == "__main__":
    main()