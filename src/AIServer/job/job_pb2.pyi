from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SupportedLanguage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ARABIC: _ClassVar[SupportedLanguage]
    CHINESE_SIMPLIFIED: _ClassVar[SupportedLanguage]
    CHINESE_TRADITIONAL: _ClassVar[SupportedLanguage]
    CZECH: _ClassVar[SupportedLanguage]
    DANISH: _ClassVar[SupportedLanguage]
    DUTCH: _ClassVar[SupportedLanguage]
    ENGLISH: _ClassVar[SupportedLanguage]
    ESTONIAN: _ClassVar[SupportedLanguage]
    FINNISH: _ClassVar[SupportedLanguage]
    FRENCH: _ClassVar[SupportedLanguage]
    GERMAN: _ClassVar[SupportedLanguage]
    HUNGARIAN: _ClassVar[SupportedLanguage]
    ITALIAN: _ClassVar[SupportedLanguage]
    JAPANESE: _ClassVar[SupportedLanguage]
    KOREAN: _ClassVar[SupportedLanguage]
    NORWEGIAN: _ClassVar[SupportedLanguage]
    POLISH: _ClassVar[SupportedLanguage]
    PORTUGUESE: _ClassVar[SupportedLanguage]
    PORTUGUESE_BRAZILIAN: _ClassVar[SupportedLanguage]
    ROMANIAN: _ClassVar[SupportedLanguage]
    RUSSIAN: _ClassVar[SupportedLanguage]
    SLOVAK: _ClassVar[SupportedLanguage]
    SPANISH: _ClassVar[SupportedLanguage]
    SPANISH_LATIN: _ClassVar[SupportedLanguage]
    SWEDISH: _ClassVar[SupportedLanguage]
    TURKISH: _ClassVar[SupportedLanguage]
    UKRAINIAN: _ClassVar[SupportedLanguage]
ARABIC: SupportedLanguage
CHINESE_SIMPLIFIED: SupportedLanguage
CHINESE_TRADITIONAL: SupportedLanguage
CZECH: SupportedLanguage
DANISH: SupportedLanguage
DUTCH: SupportedLanguage
ENGLISH: SupportedLanguage
ESTONIAN: SupportedLanguage
FINNISH: SupportedLanguage
FRENCH: SupportedLanguage
GERMAN: SupportedLanguage
HUNGARIAN: SupportedLanguage
ITALIAN: SupportedLanguage
JAPANESE: SupportedLanguage
KOREAN: SupportedLanguage
NORWEGIAN: SupportedLanguage
POLISH: SupportedLanguage
PORTUGUESE: SupportedLanguage
PORTUGUESE_BRAZILIAN: SupportedLanguage
ROMANIAN: SupportedLanguage
RUSSIAN: SupportedLanguage
SLOVAK: SupportedLanguage
SPANISH: SupportedLanguage
SPANISH_LATIN: SupportedLanguage
SWEDISH: SupportedLanguage
TURKISH: SupportedLanguage
UKRAINIAN: SupportedLanguage

class JobRequest(_message.Message):
    __slots__ = ("job_id", "time", "language", "art_description_job")
    class ArtDescriptionJob(_message.Message):
        __slots__ = ("hash_code", "xml_def", "title", "description")
        HASH_CODE_FIELD_NUMBER: _ClassVar[int]
        XML_DEF_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        hash_code: int
        xml_def: str
        title: str
        description: str
        def __init__(self, hash_code: _Optional[int] = ..., xml_def: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    ART_DESCRIPTION_JOB_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    time: _timestamp_pb2.Timestamp
    language: SupportedLanguage
    art_description_job: JobRequest.ArtDescriptionJob
    def __init__(self, job_id: _Optional[int] = ..., time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., language: _Optional[_Union[SupportedLanguage, str]] = ..., art_description_job: _Optional[_Union[JobRequest.ArtDescriptionJob, _Mapping]] = ...) -> None: ...

class JobResponse(_message.Message):
    __slots__ = ("job_id", "duration", "language", "art_description_response")
    class ArtDescriptionResponse(_message.Message):
        __slots__ = ("hash_code", "xml_def", "title", "description")
        HASH_CODE_FIELD_NUMBER: _ClassVar[int]
        XML_DEF_FIELD_NUMBER: _ClassVar[int]
        TITLE_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        hash_code: int
        xml_def: str
        title: str
        description: str
        def __init__(self, hash_code: _Optional[int] = ..., xml_def: _Optional[str] = ..., title: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    ART_DESCRIPTION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    duration: _duration_pb2.Duration
    language: SupportedLanguage
    art_description_response: JobResponse.ArtDescriptionResponse
    def __init__(self, job_id: _Optional[int] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., language: _Optional[_Union[SupportedLanguage, str]] = ..., art_description_response: _Optional[_Union[JobResponse.ArtDescriptionResponse, _Mapping]] = ...) -> None: ...
