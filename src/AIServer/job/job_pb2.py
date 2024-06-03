# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: job.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tjob.proto\x12\x03job\x1a\x1egoogle/protobuf/duration.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\x9e\x02\n\nJobRequest\x12\x0e\n\x06job_id\x18\x01 \x01(\r\x12(\n\x04time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12(\n\x08language\x18\x03 \x01(\x0e\x32\x16.job.SupportedLanguage\x12@\n\x13\x61rt_description_job\x18\x04 \x01(\x0b\x32!.job.JobRequest.ArtDescriptionJobH\x00\x1a[\n\x11\x41rtDescriptionJob\x12\x11\n\thash_code\x18\x01 \x01(\x05\x12\x0f\n\x07xml_def\x18\x02 \x01(\t\x12\r\n\x05title\x18\x03 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x04 \x01(\tB\r\n\x0bjob_payload\"\xb1\x02\n\x0bJobResponse\x12\x0e\n\x06job_id\x18\x01 \x01(\r\x12+\n\x08\x64uration\x18\x02 \x01(\x0b\x32\x19.google.protobuf.Duration\x12(\n\x08language\x18\x03 \x01(\x0e\x32\x16.job.SupportedLanguage\x12K\n\x18\x61rt_description_response\x18\x04 \x01(\x0b\x32\'.job.JobResponse.ArtDescriptionResponseH\x00\x1a`\n\x16\x41rtDescriptionResponse\x12\x11\n\thash_code\x18\x01 \x01(\x05\x12\x0f\n\x07xml_def\x18\x02 \x01(\t\x12\r\n\x05title\x18\x03 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x04 \x01(\tB\x0c\n\njob_result*\x9d\x03\n\x11SupportedLanguage\x12\n\n\x06\x41RABIC\x10\x00\x12\x16\n\x12\x43HINESE_SIMPLIFIED\x10\x01\x12\x17\n\x13\x43HINESE_TRADITIONAL\x10\x02\x12\t\n\x05\x43ZECH\x10\x03\x12\n\n\x06\x44\x41NISH\x10\x04\x12\t\n\x05\x44UTCH\x10\x05\x12\x0b\n\x07\x45NGLISH\x10\x06\x12\x0c\n\x08\x45STONIAN\x10\x07\x12\x0b\n\x07\x46INNISH\x10\x08\x12\n\n\x06\x46RENCH\x10\t\x12\n\n\x06GERMAN\x10\n\x12\r\n\tHUNGARIAN\x10\x0b\x12\x0b\n\x07ITALIAN\x10\x0c\x12\x0c\n\x08JAPANESE\x10\r\x12\n\n\x06KOREAN\x10\x0e\x12\r\n\tNORWEGIAN\x10\x0f\x12\n\n\x06POLISH\x10\x10\x12\x0e\n\nPORTUGUESE\x10\x11\x12\x18\n\x14PORTUGUESE_BRAZILIAN\x10\x12\x12\x0c\n\x08ROMANIAN\x10\x13\x12\x0b\n\x07RUSSIAN\x10\x14\x12\n\n\x06SLOVAK\x10\x15\x12\x0b\n\x07SPANISH\x10\x16\x12\x11\n\rSPANISH_LATIN\x10\x17\x12\x0b\n\x07SWEDISH\x10\x18\x12\x0b\n\x07TURKISH\x10\x19\x12\r\n\tUKRAINIAN\x10\x1a\x32=\n\nJobManager\x12/\n\nJobService\x12\x0f.job.JobRequest\x1a\x10.job.JobResponseB\t\xaa\x02\x06\x41ICoreb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'job_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\006AICore'
  _globals['_SUPPORTEDLANGUAGE']._serialized_start=681
  _globals['_SUPPORTEDLANGUAGE']._serialized_end=1094
  _globals['_JOBREQUEST']._serialized_start=84
  _globals['_JOBREQUEST']._serialized_end=370
  _globals['_JOBREQUEST_ARTDESCRIPTIONJOB']._serialized_start=264
  _globals['_JOBREQUEST_ARTDESCRIPTIONJOB']._serialized_end=355
  _globals['_JOBRESPONSE']._serialized_start=373
  _globals['_JOBRESPONSE']._serialized_end=678
  _globals['_JOBRESPONSE_ARTDESCRIPTIONRESPONSE']._serialized_start=568
  _globals['_JOBRESPONSE_ARTDESCRIPTIONRESPONSE']._serialized_end=664
  _globals['_JOBMANAGER']._serialized_start=1096
  _globals['_JOBMANAGER']._serialized_end=1157
# @@protoc_insertion_point(module_scope)