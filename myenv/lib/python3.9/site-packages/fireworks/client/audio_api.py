from enum import Enum
from typing import List, Mapping, Optional, Union
from pydantic import BaseModel, Field


class Error(BaseModel, extra="forbid"):
    object: str = "error"
    type: str = "invalid_request_error"
    message: str


class ErrorResponse(BaseModel, extra="forbid"):
    error: Error = Field(default_factory=Error)


class TranscriptionRequest(BaseModel):
    model: Optional[str] = None
    vad_model: Optional[str] = None
    alignment_model: Optional[str] = None
    diarization_model: Optional[str] = None

    prompt: Optional[str] = None
    response_format: Optional[str] = None
    temperature: Optional[Union[float, List[float]]] = None
    preprocessing: Optional[str] = None
    max_clip_len: Optional[float] = None

    language: Optional[str] = None
    timestamp_granularities: Optional[List[str]] = None
    diarize: Optional[str] = None
    min_speakers: Optional[int] = None
    max_speakers: Optional[int] = None

    def to_multipart(self) -> Mapping[str, Union[str, bytes]]:
        result = {}
        for key, value in self.model_dump(exclude_none=True).items():
            if isinstance(value, (str, bytes)):
                result[key] = value
            elif isinstance(value, list):
                result[key] = ",".join(str(e) for e in value)
            else:
                result[key] = str(value)
        return result


class TranscriptionResponse(BaseModel):
    text: str


class TranscriptionWord(BaseModel):
    word: str
    start: Optional[float]
    end: Optional[float]
    language: str
    probability: Optional[float] = None
    hallucination_score: Optional[float] = 0.0
    is_final: Optional[bool] = None
    speaker_id: Optional[str] = None


class TranscriptionSegment(BaseModel):
    id: int
    seek: int
    start: Optional[float]
    end: Optional[float]
    audio_start: Optional[float]
    audio_end: Optional[float]
    text: str
    language: str
    tokens: List[int]
    words: Optional[List[TranscriptionWord]] = None
    temperature: Optional[float] = None
    avg_logprob: Optional[float] = None
    compression_ratio: Optional[float] = None
    no_speech_prob: Optional[float] = None
    no_speech: Optional[bool] = None
    retry_count: Optional[int] = None
    speaker_id: Optional[str] = None


class TranscriptionVerboseResponse(BaseModel):
    task: str = "transcribe"  # Not documented by returned by OAI API
    language: str
    duration: Optional[float]
    text: str
    words: Optional[List[TranscriptionWord]] = None
    segments: Optional[List[TranscriptionSegment]] = None


class TranslationRequest(BaseModel):
    model: Optional[str] = None
    vad_model: Optional[str] = None
    alignment_model: Optional[str] = None

    prompt: Optional[str] = None
    response_format: Optional[str] = None
    temperature: Optional[Union[float, List[float]]] = None
    preprocessing: Optional[str] = None
    max_clip_len: Optional[float] = None

    timestamp_granularities: Optional[List[str]] = None

    def to_multipart(self) -> Mapping[str, Union[str, bytes]]:
        result = {}
        for key, value in self.model_dump(exclude_none=True).items():
            if isinstance(value, (str, bytes)):
                result[key] = value
            elif isinstance(value, list):
                result[key] = ",".join(str(e) for e in value)
            else:
                result[key] = str(value)
        return result


class AlignmentRequest(BaseModel):
    vad_model: Optional[str] = None
    alignment_model: Optional[str] = None

    text: str
    response_format: Optional[str] = None
    preprocessing: Optional[str] = None

    def to_multipart(self) -> Mapping[str, Union[str, bytes]]:
        result = {}
        for key, value in self.model_dump(exclude_none=True).items():
            if isinstance(value, (str, bytes)):
                result[key] = value
            elif isinstance(value, list):
                result[key] = ",".join(str(e) for e in value)
            else:
                result[key] = str(value)
        return result
