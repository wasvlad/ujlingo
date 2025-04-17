from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Type

from pydantic import BaseModel, Field

from database.models import User, WordTranslation
from .caching import CachingInterface


class Result(BaseModel):
    is_correct: bool
    correct_answer: str

class QuestionTypeEnum(Enum):
    base = 0
    msq = 1
    reorder = 2

class QuestionJsonBase(BaseModel):
    question: str
    type: int = Field(default=QuestionTypeEnum.base.value, description="0 - for base (this one), 1 - for MSQ, 2 - for reorder.")

class QuestionInterface(ABC):
    @abstractmethod
    def give_answer(self, answer: str) -> Result:
        pass

    @abstractmethod
    def get(self) -> QuestionJsonBase:
        pass


class KnowledgeSaverInterface(ABC):

    @abstractmethod
    def answered(self, result: Result) -> None:
        pass

    @abstractmethod
    def asked(self) -> None:
        pass


class QuestionProxyInterface(ABC):

    @abstractmethod
    def get(self) -> QuestionJsonBase:
        pass

    @abstractmethod
    def give_answer(self, answer: str) -> Result:
        pass

class QuestionProxy(QuestionProxyInterface):
    def __init__(self, question: QuestionInterface, knowledge_saver: KnowledgeSaverInterface):
        self._question = question
        self._knowledge_saver = knowledge_saver
        self._asked = False

    def get(self) -> QuestionJsonBase:
        if not self._asked:
            self._knowledge_saver.asked()
            self._asked = True
        return self._question.get()

    def give_answer(self, answer: str) -> Result:
        result = self._question.give_answer(answer)
        self._knowledge_saver.answered(result)
        self._asked = False
        return result


class NoQuestionsException(Exception):
    pass


class Test:
    _questions = []
    _current_question = 0
    _user: User

    def __init__(self, user: User, questions: List[QuestionProxyInterface],
                 caching_class: Type[CachingInterface] | None = None):
        self._questions = questions
        self._user = user
        self._current_question = 0
        if caching_class is None:
            self._caching = None
        else:
            self._caching = caching_class(f"tests:user:{user.id}", self)
            self._caching.write()

    def get_question(self) -> QuestionJsonBase | None:
        if self._current_question >= len(self._questions):
            if self._caching is not None:
                self._caching.delete()
            return None
        return self._questions[self._current_question].get()

    def give_answer(self, answer: str):
        if self._current_question >= len(self._questions):
            if self._caching is not None:
                self._caching.delete()
            raise NoQuestionsException("No more questions")
        question = self._questions[self._current_question]
        result = question.give_answer(answer)
        self._current_question += 1
        if self._caching is not None:
            self._caching.update()
        return result

    def delete(self):
        self._current_question = len(self._questions)
        if self._caching is not None:
            self._caching.delete()

    @staticmethod
    def load_from_cache(user: User, caching_class: Type[CachingInterface]) -> 'Test':
        instance: Test = caching_class.load(f"tests:user:{user.id}")
        return instance
