from abc import ABC, abstractmethod
from typing import Dict, Any, List
from database.models import User

from pydantic import BaseModel

class Result(BaseModel):
    is_correct: bool
    correct_answer: str

class QuestionJsonBase(BaseModel):
    question: str

class QuestionInterface(ABC):
    @abstractmethod
    def give_answer(self, answer: str) -> Result:
        pass

    @abstractmethod
    def get(self) -> QuestionJsonBase:
        pass


class NoQuestionsException(Exception):
    pass


class Test:
    _questions = []
    _current_question = 0
    _user: User

    def __init__(self, user: User, questions: List[QuestionInterface]):
        self._questions = questions
        self._user = user
        self._current_question = 0

    def get_question(self) -> QuestionJsonBase | None:
        if self._current_question >= len(self._questions):
            return None
        return self._questions[self._current_question].get()

    def give_answer(self, answer: str):
        if self._current_question >= len(self._questions):
            raise NoQuestionsException("No more questions")
        question = self._questions[self._current_question]
        result = question.give_answer(answer)
        self._current_question += 1
        return result