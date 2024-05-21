# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: job.proto
# plugin: grpclib.plugin.main
import abc
import typing

import grpclib.client
import grpclib.const

if typing.TYPE_CHECKING:
    import grpclib.server

from google.protobuf import duration_pb2, timestamp_pb2

from . import job_pb2


class JobManagerBase(abc.ABC):

    @abc.abstractmethod
    async def JobService(self, stream: 'grpclib.server.Stream[job_pb2.JobRequest, job_pb2.JobResponse]') -> None:
        pass

    def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:
        return {
            '/job.JobManager/JobService': grpclib.const.Handler(
                self.JobService,
                grpclib.const.Cardinality.UNARY_UNARY,
                job_pb2.JobRequest,
                job_pb2.JobResponse,
            ),
        }


class JobManagerStub:

    def __init__(self, channel: grpclib.client.Channel) -> None:
        self.JobService = grpclib.client.UnaryUnaryMethod(
            channel,
            '/job.JobManager/JobService',
            job_pb2.JobRequest,
            job_pb2.JobResponse,
        )