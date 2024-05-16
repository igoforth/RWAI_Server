from typing import ClassVar as _ClassVar
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import message as _message
from google.protobuf import timestamp_pb2 as _timestamp_pb2

DESCRIPTOR: _descriptor.FileDescriptor

class JobRequest(_message.Message):
    __slots__ = ("job_id", "job_type", "time", "payload")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    job_type: str
    time: _timestamp_pb2.Timestamp
    payload: bytes
    def __init__(self, job_id: _Optional[int] = ..., job_type: _Optional[str] = ..., time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., payload: _Optional[bytes] = ...) -> None: ...

class JobResponse(_message.Message):
    __slots__ = ("job_id", "job_type", "duration", "payload")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_TYPE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    job_type: str
    duration: _duration_pb2.Duration
    payload: bytes
    def __init__(self, job_id: _Optional[int] = ..., job_type: _Optional[str] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., payload: _Optional[bytes] = ...) -> None: ...
