import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "govee_light_ble"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


api_utils = load("api_utils", ROOT / "api_utils.py")
const = load("const", ROOT / "const.py")


def main() -> None:
    assert const.default_segmented("ihoment_H6102_C796") is False
    assert const.default_segmented("Govee_H6061_171D") is True
    assert api_utils.brightness_to_device(255, segmented=False) == 255
    assert api_utils.brightness_to_device(255, segmented=True) == 100
    assert api_utils.brightness_to_device(1, segmented=True) == 1
    assert api_utils.brightness_from_device(100, segmented=True) == 255
    assert api_utils.brightness_from_device(300, segmented=False) == 255


if __name__ == "__main__":
    main()
