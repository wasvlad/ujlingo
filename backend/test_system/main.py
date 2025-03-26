from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type

from database import get_db
from database.models import User, WordTranslation, Word

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


class WordsTranslationQuestion(QuestionInterface):
    _word_translation: WordTranslation

    def __init__(self, translation: WordTranslation):
        self._word_translation = translation
        self._word_translation.word_original = translation.word_original
        self._word_translation.word_translated = translation.word_translated

    def give_answer(self, answer: str) -> Result:
        db = next(get_db())
        word = db.query(Word).filter(Word.word == answer).first()
        if word is None:
            result = Result(is_correct=False, correct_answer=self._word_translation.word_translated.word)
            return result
        word_original = self._word_translation.word_original
        word_translation = db.query(WordTranslation).filter(WordTranslation.word_original_id == word_original.id,
                                                            WordTranslation.word_translated_id == word.id).first()
        if word_translation is None:
            result = Result(is_correct=False, correct_answer=self._word_translation.word_translated.word)
            return result
        is_correct = True
        result = Result(is_correct=is_correct, correct_answer=self._word_translation.word_translated.word)
        return result

    def get(self) -> QuestionJsonBase:
        result = QuestionJsonBase(question="Translate the word: " + self._word_translation.word_original.word)
        return result


class CachingInterface(ABC):
    def __init__(self, key: str, data: Any):
        self.key = key
        self.data = data

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def read(self) -> Any:
        pass

    @abstractmethod
    def update(self):
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