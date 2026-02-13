from abc import ABC, abstractmethod

from ..context import PipelineContext


class BasePipelineStage(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        raise NotImplementedError
