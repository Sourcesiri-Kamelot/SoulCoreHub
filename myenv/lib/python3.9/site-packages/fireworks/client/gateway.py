# Copyright (c) Fireworks AI, Inc. and affiliates.
#
# All Rights Reserved.

import configparser
import os
import subprocess
from typing import Any, Callable, List, Optional
import grpc
from fireworks.client.log import log_warning
from fireworks.protos.generated.gateway.gateway_pb2_grpc import GatewayStub
from fireworks.protos.generated.gateway.model_pb2 import (
    CreateModelRequest,
    DeleteModelRequest,
    GetModelRequest,
    ListModelsRequest,
    Model,
)


def _get_token_from_firectl() -> str:
    """
    Attempts to obtain auth token from firectl.

    Returns:
        token returned by firectl or an empty string if
        missing.
    """
    try:
        result = subprocess.run(["firectl", "token"], capture_output=True, text=True)
    except:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout


def _get_token_from_env() -> str:
    """
    Attempts to obtain auth token from the environment variable.

    Returns:
        token retrieved from env variable or an empty string if
        missing.
    """
    return os.environ.get("FIREWORKS_API_TOKEN", "")


def _get_token_from_config() -> str:
    """
    Attempts to obtain auth token from the config file.

    Returns:
        token retrieved from the config or an empty string if
        missing.
    """
    path = os.path.expanduser("~/.fireworks/auth.ini")
    try:
        with open(path, "r") as f:
            content = "[dummy_section]\n" + f.read()
        config = configparser.ConfigParser()
        config.read_string(content)
        return config.get("dummy_section", "id_token")
    except:
        return ""


def _call_with_token_refresh(func: Callable) -> Callable:
    """
    If the initial fuction invocation fails with an authentication error,
    attempts to refresh the credentials and retry the call.

    It is meant to be used as a decorator attached to grpc client wrappers.

    Args:
        func: the function performing grpc call.

    Returns:
        wrapper around the input function.
    """

    def _func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAUTHENTICATED:
                log_warning("Token is not valid. Will attempt a refresh")
                connect = getattr(args[0], "_connect")
                connect(
                    [
                        _get_token_from_firectl,
                        _get_token_from_config,
                        _get_token_from_env,
                    ]
                )
        return func(*args, **kwargs)

    return _func


class Gateway(GatewayStub):
    """
    Control plane gateway client that exposes its endpoints through
    convenient APIs.

    Keep the API consistent with `gateway.proto`.
    """

    def __init__(self, *, server_addr: str = "gateway.fireworks.ai:443") -> None:
        """
        Args:
            server_addr: the network address of the gateway server.
        """
        self._server_addr = server_addr
        self._connect()

    def _connect(self, sources: Optional[List[Callable]] = None) -> None:
        """
        Obtains credentials and creates a stub connecting to the gateway.

        Args:
            sources: the list of authentication token sources.
        """
        if sources is None:
            sources = [
                _get_token_from_env,
                _get_token_from_config,
                _get_token_from_firectl,
            ]
        token = ""
        for source in sources:
            token = source()
            if token:
                break
        if not token:
            raise RuntimeError(
                "cannot find fireworks API token. To obtain it, install `firectl` "
                "following the instructions at https://fireworks.ai/docs/install/ "
                "and call `firectl signin <FIREWORKS_ACCOUNT_ID>`. Alternatively, "
                "you can set FIREWORKS_API_TOKEN environment variable"
            )
        creds = grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(), grpc.access_token_call_credentials(token)
        )
        channel = grpc.secure_channel(self._server_addr, creds)
        self._stub = GatewayStub(channel)

    @_call_with_token_refresh
    def create_model(
        self, *, parent: str = "", model: Optional[Model] = None, model_id: str = ""
    ) -> Model:
        """
        Creates a model.

        Args:
            parent: resource name of the parent account,
            model: properties of the model being created,
            model_id: id of the model.

        Returns:
            properties of the created model.
        """
        request = CreateModelRequest()
        request.parent = parent
        request.model = model
        request.model_id = model_id
        return self._stub.CreateModel(request)

    @_call_with_token_refresh
    def get_model(self, *, name: str = "") -> Model:
        """
        Obtains proprties of a model.

        Args:
            name: resource name of the model.

        Returns:
            properties of the model with the given name.
        """
        request = GetModelRequest()
        request.name = name
        return self._stub.GetModel(request)

    @_call_with_token_refresh
    def delete_model(self, *, name: str = "") -> None:
        """
        Deletes a model.

        Args:
            name: resource name of the model to delete.
        """
        request = DeleteModelRequest()
        request.name = name
        self._stub.DeleteModel(request)

    @_call_with_token_refresh
    def list_models(
        self,
        *,
        parent: str = "",
        filter: str = "",
        order_by: str = "",
    ) -> List[Model]:
        """
        Fetches the list of available models.

        Args:
            parent: resource name of the parent account,
            filter: only models satisfying the provided filter (if specified)
                will be returned. See https://google.aip.dev/160 for the filter
                grammar,
            order_by: a comma-separated list of fields to order by. e.g. "foo,bar".
                The default sort order is ascending. To specify a descending order
                for a field, append a " desc" suffix. e.g. "foo desc,bar"
                Subfields are specified with a "." character. e.g. "foo.bar".
                If not specified, the default order is by "name".

        Returns:
            list of models satisfying the retrieval criteria.
        """
        result = []
        page_token = None
        while True:
            request = ListModelsRequest()
            request.parent = parent
            request.filter = filter
            request.order_by = order_by
            if page_token is not None:
                request.page_token = page_token
            response = self._stub.ListModels(request)
            result.extend(response.models)
            if response.total_size < len(result):
                return result
                # FIXME(pawel): there is a bug in the control plane code
                # that causes inconsistency between the total_size and the
                # result size. Uncomment the line below after it gets fixed.
                # raise ValueError(
                #     f"response total size {response.total_size} is lower than the "
                #     f"result length {len(result)}")
            elif response.total_size == len(result):
                return result
            page_token = response.next_page_token
