import httpx
import asyncio
import os

from urllib.parse import urlparse
from typing import List, Optional, Union

from .audio_api import (
    AlignmentRequest,
    TranscriptionRequest,
    TranslationRequest,
    TranscriptionResponse,
    TranscriptionVerboseResponse,
)
from .api_client import FireworksClient


UrlPath = str


class AudioInference(FireworksClient):
    """
    Main client class for the Fireworks Audio Generation APIs.
    """

    def __init__(
        self,
        model: str = "whisper-v3",
        vad_model: str = "silero",
        alignment_model: str = "tdnn_ffn",
        diarization_model: str = "pyannote",
        request_timeout=600,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(request_timeout, api_key=api_key, base_url=base_url, **kwargs)
        self.model = model
        self.vad_model = vad_model
        self.alignment_model = alignment_model
        self.diarization_model = diarization_model

    @staticmethod
    def _audio_to_bytes(audio: Union[str, os.PathLike, UrlPath, bytes]) -> bytes:
        def is_url(path: str) -> bool:
            try:
                parsed = urlparse(path)
                return bool(parsed.scheme) and bool(parsed.netloc)
            except:
                return False

        if is_url(audio):
            return audio.encode("utf-8")
        elif isinstance(audio, (str, os.PathLike)):
            with open(audio, "rb") as f:
                audio = f.read()
        return audio

    def transcribe(
        self,
        audio: Union[str, os.PathLike, bytes, UrlPath],
        model: str = None,
        vad_model: str = None,
        alignment_model: str = None,
        diarization_model: str = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[Union[float, List[float]]] = None,
        preprocessing: Optional[str] = None,
        max_clip_len: Optional[float] = None,
        language: Optional[str] = None,
        timestamp_granularities: Optional[List[str]] = None,
        diarize: Optional[str] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
    ) -> TranscriptionResponse:
        """
        Transcribe an audio into text using ASR (audio speech recognition).
        See the OpenAPI spec (https://docs.fireworks.ai/api-reference/audio-transcriptions)
        for the most up-to-date description of the supported parameters

        Parameters:
        - audio (Union[str, os.PathLike, bytes, UrlPath]): An audio to transcribe.
        - model (str, optional): The ASR model name to call. If not present, defaults to `self.model` on the AudioInference object.
        - vad_model (str, optional): The VAD model name to call. If not present, defaults to `self.vad_model` on the AudioInference object.
        - alignment_model (str, optional): The alignment model name to call. If not present, defaults to `self.alignment_model` on the AudioInference object.
        - diarization_model (str, optional): The diarization model name to call. If not present, defaults to `self.diarization_model` on the AudioInference object.
        - prompt (str, optional): The input prompt with which to prime transcription. This can be used, for example, to continue a prior transcription given new audio data.
        - response_format (str): The format in which to return the response. Can be one of "json", "text", "srt", "verbose_json", or "vtt". If not present, defaults to "json".
        - temperature (Union[float, List[float]], optional): Sampling temperature to use when decoding text tokens during transcription. Alternatively, a list of temperatures to enable fallback decoding. If not present, defaults to "0.0".
        - preprocessing (str, optional): The preprocessing to apply. Can be one of "none", "dynamic", "soft_dynamic", "bass_dynamic". If not present, defaults to "none".
        - max_clip_len (float, optional): The desired maximum length of audio segment.
        - language (str, optional): The target languages for transcription. The set of supported target languages can be found at https://tinyurl.com/bdz3y63b.
        - timestamp_granularities (List[str], optional): The timestamp granularities to populate for this transcription. `response_format` must be set "verbose_json" to use timestamp granularities. Either or both of these options are supported: "word", or "segment". If not present, defaults to "segment".
        - diarize (str, optional): Whether to get speaker diarization for the audio. Can be one of "true", or "false". `response_format` must be set "verbose_json" and `timestamp_granularities` must include "word" to use diarization. If not present, defaults to "false".
        - min_speakers (int, optional): The minimum number of expected speakers for diarization. `diarize` must be set "true" to use `min_speakers`.
        - max_speakers (int, optional): The maximum number of expected speakers for diarization. `diarize` must be set "true" to use `max_speakers`.

        Returns:
        TranscriptionResponse: An object with transcription.

        Raises:
        RuntimeError: If there is an error in the audio transcription process.
        """
        return asyncio.run(
            self.transcribe_async(
                audio,
                model,
                vad_model,
                alignment_model,
                diarization_model,
                prompt,
                response_format,
                temperature,
                preprocessing,
                max_clip_len,
                language,
                timestamp_granularities,
                diarize,
                min_speakers,
                max_speakers,
            )
        )

    async def transcribe_async(
        self,
        audio: Union[str, os.PathLike, bytes, UrlPath],
        model: str = None,
        vad_model: str = None,
        alignment_model: str = None,
        diarization_model: str = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[Union[float, List[float]]] = None,
        preprocessing: Optional[str] = None,
        max_clip_len: Optional[float] = None,
        language: Optional[str] = None,
        timestamp_granularities: Optional[List[str]] = None,
        diarize: Optional[str] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
    ) -> Union[TranscriptionResponse, TranscriptionVerboseResponse, str]:
        """
        Transcribe an audio into text using ASR (audio speech recognition).
        See the OpenAPI spec (https://docs.fireworks.ai/api-reference/audio-transcriptions)
        for the most up-to-date description of the supported parameters

        Parameters:
        - audio (Union[str, os.PathLike, bytes, UrlPath]): An audio to transcribe.
        - model (str, optional): The ASR model name to call. If not present, defaults to `self.model` on the AudioInference object.
        - vad_model (str, optional): The VAD model name to call. If not present, defaults to `self.vad_model` on the AudioInference object.
        - alignment_model (str, optional): The alignment model name to call. If not present, defaults to `self.alignment_model` on the AudioInference object.
        - diarization_model (str, optional): The diarization model name to call. If not present, defaults to `self.diarization_model` on the AudioInference object.
        - prompt (str, optional): The input prompt with which to prime transcription. This can be used, for example, to continue a prior transcription given new audio data.
        - response_format (str): The format in which to return the response. Can be one of "json", "text", "srt", "verbose_json", or "vtt". If not present, defaults to "json".
        - temperature (Union[float, List[float]], optional): Sampling temperature to use when decoding text tokens during transcription. Alternatively, a list of temperatures to enable fallback decoding. If not present, defaults to "0.0".
        - preprocessing (str, optional): The preprocessing to apply. Can be one of "none", "dynamic", "soft_dynamic", "bass_dynamic". If not present, defaults to "none".
        - max_clip_len (float, optional): The desired maximum length of audio segment.
        - language (str, optional): The target languages for transcription. The set of supported target languages can be found at https://tinyurl.com/bdz3y63b.
        - timestamp_granularities (List[str], optional): The timestamp granularities to populate for this transcription. `response_format` must be set "verbose_json" to use timestamp granularities. Either or both of these options are supported: "word", or "segment". If not present, defaults to "segment".
        - diarize (str, optional): Whether to get speaker diarization for the audio. Can be one of "true", or "false". `response_format` must be set "verbose_json" and `timestamp_granularities` must include "word" to use diarization. If not present, defaults to "false".
        - min_speakers (int, optional): The minimum number of expected speakers for diarization. `diarize` must be set "true" to use `min_speakers`.
        - max_speakers (int, optional): The maximum number of expected speakers for diarization. `diarize` must be set "true" to use `max_speakers`.

        Returns:
        TranscriptionResponse: An object with transcription.

        Raises:
        RuntimeError: If there is an error in the audio transcription process.
        """
        request = TranscriptionRequest(
            model=model or self.model,
            vad_model=vad_model or self.vad_model,
            alignment_model=alignment_model or self.alignment_model,
            diarization_model=diarization_model or self.diarization_model,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
            preprocessing=preprocessing,
            max_clip_len=max_clip_len,
            language=language,
            timestamp_granularities=timestamp_granularities,
            diarize=diarize,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
        )
        data = {
            **request.to_multipart(),
        }
        files = {
            "file": self._audio_to_bytes(audio),
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/v1/audio/transcriptions"
            response = await client.post(endpoint_base_uri, data=data, files=files)
            self._error_handling(response)

            if response_format in [None, "json"]:
                return TranscriptionResponse(**response.json())
            elif response_format == "verbose_json":
                return TranscriptionVerboseResponse(**response.json())
            else:
                return response.text

    def translate(
        self,
        audio: Union[str, os.PathLike, bytes, UrlPath],
        model: str = None,
        vad_model: str = None,
        alignment_model: str = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[Union[float, List[float]]] = None,
        preprocessing: Optional[str] = None,
        max_clip_len: Optional[float] = None,
        timestamp_granularities: Optional[List[str]] = None,
    ) -> TranscriptionResponse:
        """
        Translate an audio into english text using ASR (audio speech recognition).
        See the OpenAPI spec (https://docs.fireworks.ai/api-reference/audio-translations)
        for the most up-to-date description of the supported parameters

        Parameters:
        - audio (Union[str, os.PathLike, bytes, UrlPath]): An audio to translate.
        - model (str, optional): The ASR model name to call. If not present, defaults to `self.model` on the AudioInference object.
        - vad_model (str, optional): The VAD model name to call. If not present, defaults to `self.vad_model` on the AudioInference object.
        - alignment_model (str, optional): The alignment model name to call. If not present, defaults to `self.alignment_model` on the AudioInference object.
        - prompt (str, optional): The input prompt with which to prime transcription. This can be used, for example, to continue a prior transcription given new audio data.
        - response_format (str): The format in which to return the response. Can be one of "json", "text", "srt", "verbose_json", or "vtt". If not present, defaults to "json".
        - temperature (Union[float, List[float]], optional): Sampling temperature to use when decoding text tokens during transcription. Alternatively, a list of temperatures to enable fallback decoding. If not present, defaults to "0.0".
        - preprocessing (str, optional): The preprocessing to apply. Can be one of "none", "dynamic", "soft_dynamic", "bass_dynamic". If not present, defaults to "none".
        - max_clip_len (float, optional): The desired maximum length of audio segment.
        - timestamp_granularities (List[str], optional): The timestamp granularities to populate for this transcription. `response_format` must be set "verbose_json" to use timestamp granularities. Either or both of these options are supported: "word", or "segment". If not present, defaults to "segment".

        Returns:
        TranscriptionResponse: An object with english transcription.

        Raises:
        RuntimeError: If there is an error in the audio transcription process.
        """
        return asyncio.run(
            self.translate_async(
                audio,
                model,
                vad_model,
                alignment_model,
                prompt,
                response_format,
                temperature,
                preprocessing,
                max_clip_len,
                timestamp_granularities,
            )
        )

    async def translate_async(
        self,
        audio: Union[str, os.PathLike, bytes, UrlPath],
        model: str = None,
        vad_model: str = None,
        alignment_model: str = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[Union[float, List[float]]] = None,
        preprocessing: Optional[str] = None,
        max_clip_len: Optional[float] = None,
        timestamp_granularities: Optional[List[str]] = None,
    ) -> Union[TranscriptionResponse, TranscriptionVerboseResponse, str]:
        """
        Translate an audio into english text using ASR (audio speech recognition).
        See the OpenAPI spec (https://docs.fireworks.ai/api-reference/audio-translations)
        for the most up-to-date description of the supported parameters

        Parameters:
        - audio (Union[str, os.PathLike, bytes, UrlPath]): An audio to translate.
        - model (str, optional): The ASR model name to call. If not present, defaults to `self.model` on the AudioInference object.
        - vad_model (str, optional): The VAD model name to call. If not present, defaults to `self.vad_model` on the AudioInference object.
        - alignment_model (str, optional): The alignment model name to call. If not present, defaults to `self.alignment_model` on the AudioInference object.
        - prompt (str, optional): The input prompt with which to prime transcription. This can be used, for example, to continue a prior transcription given new audio data.
        - response_format (str): The format in which to return the response. Can be one of "json", "text", "srt", "verbose_json", or "vtt". If not present, defaults to "json".
        - temperature (Union[float, List[float]], optional): Sampling temperature to use when decoding text tokens during transcription. Alternatively, a list of temperatures to enable fallback decoding. If not present, defaults to "0.0".
        - timestamp_granularities (List[str]): The timestamp granularities to populate for this transcription. `response_format` must be set "verbose_json" to use timestamp granularities. Either or both of these options are supported: "word", or "segment". If not present, defaults to "segment".
        - preprocessing (str, optional): The preprocessing to apply. Can be one of "none", "dynamic", "soft_dynamic", "bass_dynamic". If not present, defaults to "none".
        - max_clip_len (float, optional): The desired maximum length of audio segment.
        - timestamp_granularities (List[str], optional): The timestamp granularities to populate for this transcription. `response_format` must be set "verbose_json" to use timestamp granularities. Either or both of these options are supported: "word", or "segment". If not present, defaults to "segment".

        Returns:
        TranscriptionResponse: An object with english transcription.

        Raises:
        RuntimeError: If there is an error in the audio transcription process.
        """
        request = TranslationRequest(
            model=model or self.model,
            vad_model=vad_model or self.vad_model,
            alignment_model=alignment_model or self.alignment_model,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
            preprocessing=preprocessing,
            max_clip_len=max_clip_len,
            timestamp_granularities=timestamp_granularities,
        )
        data = {
            **request.to_multipart(),
        }
        files = {
            "file": self._audio_to_bytes(audio),
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/v1/audio/translations"
            response = await client.post(endpoint_base_uri, data=data, files=files)
            self._error_handling(response)

            if response_format in [None, "json"]:
                return TranscriptionResponse(**response.json())
            elif response_format == "verbose_json":
                return TranscriptionVerboseResponse(**response.json())
            else:
                return response.text

    def align(
        self,
        audio: Union[str, os.PathLike, bytes, UrlPath],
        text: str,
        vad_model: str = None,
        alignment_model: str = None,
        response_format: Optional[str] = None,
        preprocessing: Optional[str] = None,
    ) -> Union[TranscriptionResponse, TranscriptionVerboseResponse, str]:
        """
        Align an audio into text using ASR (audio speech recognition).

        Parameters:
        - audio (Union[str, os.PathLike, bytes, UrlPath]): An audio to align.
        - text (str): The text to align to the audio.
        - vad_model (str, optional): The VAD model name to call. If not present, defaults to `self.vad_model` on the AudioInference object.
        - alignment_model (str, optional): The alignment model name to call. If not present, defaults to `self.alignment_model` on the AudioInference object.
        - response_format (str): The format in which to return the response. Can be one of  "srt", "verbose_json", or "vtt". If not present, defaults to "verbose_json".
        - preprocessing (str, optional): The preprocessing to apply. Can be one of "none", "dynamic", "soft_dynamic", "bass_dynamic". If not present, defaults to "none".

        Returns:
        TranscriptionResponse: An object with transcription.

        Raises:
        RuntimeError: If there is an error in the audio transcription process.
        """
        return asyncio.run(
            self.align_async(
                audio,
                text,
                vad_model,
                alignment_model,
                response_format,
                preprocessing,
            )
        )

    async def align_async(
        self,
        audio: Union[str, os.PathLike, bytes, UrlPath],
        text: str,
        vad_model: str = None,
        alignment_model: str = None,
        response_format: Optional[str] = None,
        preprocessing: Optional[str] = None,
    ) -> Union[TranscriptionResponse, TranscriptionVerboseResponse, str]:
        """
        Align an audio into text using ASR (audio speech recognition).

        Parameters:
        - audio (Union[str, os.PathLike, bytes, UrlPath]): An audio to align.
        - text (str): The text to align to the audio.
        - vad_model (str, optional): The VAD model name to call. If not present, defaults to `self.vad_model` on the AudioInference object.
        - alignment_model (str, optional): The alignment model name to call. If not present, defaults to `self.alignment_model` on the AudioInference object.
        - response_format (str): The format in which to return the response. Can be one of  "srt", "verbose_json", or "vtt". If not present, defaults to "verbose_json".
        - preprocessing (str, optional): The preprocessing to apply. Can be one of "none", "dynamic", "soft_dynamic", "bass_dynamic". If not present, defaults to "none".

        Returns:
        TranscriptionResponse: An object with transcription.

        Raises:
        RuntimeError: If there is an error in the audio transcription process.
        """
        request = AlignmentRequest(
            text=text,
            vad_model=vad_model or self.vad_model,
            alignment_model=alignment_model or self.alignment_model,
            response_format=response_format,
            preprocessing=preprocessing,
        )
        data = {
            **request.to_multipart(),
        }
        files = {
            "file": self._audio_to_bytes(audio),
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/v1/audio/alignments"
            response = await client.post(endpoint_base_uri, data=data, files=files)
            self._error_handling(response)

            if response_format in [None, "verbose_json"]:
                return TranscriptionVerboseResponse(**response.json())
            else:
                return response.text
