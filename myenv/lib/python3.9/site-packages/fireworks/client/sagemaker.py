import io
from typing import Dict, Generator, List, Type, Union
import json
from pydantic import BaseModel
from .api_client import FireworksClient
from .api import (
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    CompletionResponse,
    CompletionStreamResponse,
)


def _non_streaming_call(
    sagemaker_runtime,
    endpoint: str,
    inference_id: str,
    body: dict,
):
    assert body["stream"] == False
    args = {
        "EndpointName": endpoint,
        "ContentType": "application/json",
        "Body": bytes(json.dumps(body), "utf-8"),
    }
    if inference_id is not None:
        args["InferenceId"] = inference_id
    response = sagemaker_runtime.invoke_endpoint(**args)
    return json.loads(response["Body"].read().decode("utf-8"))


class _StreamIterator:
    """
    A helper class for parsing the byte stream input.

    Adapted from https://aws.amazon.com/blogs/machine-learning/elevating-the-generative-ai-experience-introducing-streaming-support-in-amazon-sagemaker-hosting/

    The output of the model will be in the following format:
    ```
    b'data: {"outputs": [" a"]}\n'
    b'data: {"outputs": [" challenging"]}\n'
    b'data: {"outputs": [" problem"]}\n'
    b'data: DONE\n'
    ...
    ```

    While usually each PayloadPart event from the event stream will contain a byte array
    with a full json, this is not guaranteed and some of the json objects may be split across
    PayloadPart events. For example:
    ```
    {'PayloadPart': {'Bytes': b'data: {"outputs": '}}
    {'PayloadPart': {'Bytes': b'[" problem"]}\n'}}
    ```

    This class accounts for this by concatenating bytes written via the 'write' function
    and then exposing a method which will return lines (ending with a '\n' character) within
    the buffer via the 'scan_lines' function. It maintains the position of the last read
    position to ensure that previous bytes are not exposed again.
    """

    def __init__(self, stream):
        self.byte_iterator = iter(stream)
        self.buffer = io.BytesIO()
        self.read_pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            self.buffer.seek(self.read_pos)
            line = self.buffer.readline()
            if line and line[-1] == ord("\n"):
                self.read_pos += len(line)
                line = line.strip()
                if line == b"":
                    continue
                if not line.startswith(b"data: "):
                    raise RuntimeError(
                        "Unexpected line not starting with 'data: ': " + line
                    )
                line = line.removeprefix(b"data: ")
                if line == b"[DONE]":
                    raise StopIteration
                payload = json.loads(line.decode("utf-8"))
                return payload
            try:
                chunk = next(self.byte_iterator)
            except StopIteration:
                if self.read_pos < self.buffer.getbuffer().nbytes:
                    continue
                raise
            assert "PayloadPart" in chunk, "Unknown event type:" + chunk
            self.buffer.seek(0, io.SEEK_END)
            self.buffer.write(chunk["PayloadPart"]["Bytes"])


def _streaming_call(
    sagemaker_runtime,
    endpoint: str,
    inference_id: str,
    body: dict,
):
    assert body["stream"] == True
    args = {
        "EndpointName": endpoint,
        "ContentType": "application/json",
        "Body": bytes(json.dumps(body), "utf-8"),
    }
    if inference_id is not None:
        args["InferenceId"] = inference_id
    response = sagemaker_runtime.invoke_endpoint_with_response_stream(**args)
    return _StreamIterator(response["Body"])


def invoke_completion(
    sagemaker_runtime,
    endpoint: str,
    prompt: str,
    *,
    stream: bool = False,
    inference_id: str = None,
    **kwargs,
) -> Union[CompletionResponse, Generator[CompletionStreamResponse, None, None]]:
    """
    Invoke a completion endpoint exposed from sagemaker

    Args:
      sagemaker_runtime: SageMaker runtime client (botocore.client.SageMakerRuntime).
      endpoint (str): Sagemaker endpoint to invoke.
      inference_id (str, optional): SageMaker Inference ID

      prompt (str): The prompt for Completion.
      stream (bool, optional): Whether to use streaming or not. Determines the return type. Defaults to False.
      **kwargs: any Fireworks.ai API arguments (except for "model")

    Returns:
      Union[CompletionResponse, Generator[CompletionStreamResponse, None, None]]:
        Depending on the `stream` argument, either returns a CompletionResponse
        or a generator yielding CompletionStreamResponse.

    Raises:
        botocore.errorfactory.ModelError: encapsulates all errors from the container (note that specific fireworks.client.error exceptions are not raised)
    """
    body = {"prompt": prompt, "stream": stream, **kwargs}
    if stream:
        return map(
            lambda d: CompletionStreamResponse(**d),
            _streaming_call(sagemaker_runtime, endpoint, inference_id, body),
        )
    else:
        return CompletionResponse(
            **_non_streaming_call(sagemaker_runtime, endpoint, inference_id, body)
        )


def invoke_chat_completion(
    sagemaker_runtime,
    endpoint: str,
    messages: List[Dict[str, str]],
    *,
    stream: bool = False,
    inference_id: str = None,
    **kwargs,
) -> Union[ChatCompletionResponse, Generator[ChatCompletionStreamResponse, None, None]]:
    """
    Invoke a chat completion endpoint exposed from sagemaker

    Args:
      sagemaker_runtime: SageMaker runtime client (botocore.client.SageMakerRuntime).
      endpoint (str): Sagemaker endpoint to invoke.
      inference_id (str, optional): SageMaker Inference ID

      messages (str): The previous chat history, e.g. [{"role": "system", "content": "Be nice"}, {"role": "user", "content": "Tell me a joke"}]
      stream (bool, optional): Whether to use streaming or not. Determines the return type. Defaults to False.
      **kwargs: any Fireworks.ai API arguments (except for "model")

    Returns:
      Union[ChatCompletionResponse, Generator[ChatCompletionStreamResponse, None, None]]:
        Depending on the `stream` argument, either returns a ChatCompletionResponse
        or a generator yielding ChatCompletionStreamResponse.

    Raises:
        botocore.errorfactory.ModelError: encapsulates all errors from the container (note that specific fireworks.client.error exceptions are not raised)
    """
    body = {"messages": messages, "stream": stream, **kwargs}
    if stream:
        return map(
            lambda d: ChatCompletionStreamResponse(**d),
            _streaming_call(sagemaker_runtime, endpoint, inference_id, body),
        )
    else:
        return ChatCompletionResponse(
            **_non_streaming_call(sagemaker_runtime, endpoint, inference_id, body)
        )
