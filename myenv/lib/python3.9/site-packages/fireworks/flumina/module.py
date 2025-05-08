from abc import abstractmethod
import os
import torch
from contextlib import contextmanager
from dataclasses import dataclass
import enum
from typing import Dict, Optional


class FluminaModule(torch.nn.Module):
    # Addon interface
    @abstractmethod
    def load_addon(
        self,
        addon_account_id: str,
        addon_model_id: str,
        addon_type: str,
        addon_data_path: os.PathLike,
    ): ...

    @abstractmethod
    def unload_addon(
        self,
        addon_account_id: str,
        addon_model_id: str,
        addon_type: str,
    ): ...

    @abstractmethod
    def activate_addon(
        self,
        addon_account_id: str,
        addon_model_id: str,
    ): ...

    @abstractmethod
    def deactivate_addon(
        self,
        addon_account_id: str,
        addon_model_id: str,
    ): ...


@dataclass
class _MaterializedModule:
    module: FluminaModule
    path_to_method_name: Dict[str, str]


class _ExecMode(enum.Enum):
    NONE = 0
    VALIDATE = 1
    SERVE = 2


_exec_mode = _ExecMode.NONE
_materialized_module: Optional[_MaterializedModule] = None


def _get_materialized_module():
    global _materialized_module
    em = _materialized_module
    _materialized_module = None
    return em


@contextmanager
def _with_exec_mode(mode):
    global _exec_mode
    old_mode = _exec_mode
    _exec_mode = mode
    try:
        yield
    finally:
        _exec_mode = old_mode


def main(m: FluminaModule):
    if _exec_mode == _ExecMode.NONE:
        pass
    elif _exec_mode in {_ExecMode.VALIDATE, _ExecMode.SERVE}:
        assert isinstance(
            m, FluminaModule
        ), "Argument to flumina.main() must be an instance of FluminaModule"
        path_to_method_name: Dict[str, str] = {}
        for k in dir(m):
            v = getattr(m, k)
            if hasattr(v, "_flumina_route"):
                path_to_method_name[v._flumina_route] = k

        global _materialized_module
        _materialized_module = _MaterializedModule(
            module=m,
            path_to_method_name=path_to_method_name,
        )
    else:
        raise NotImplementedError("Unsupported ExecMode", _exec_mode)
