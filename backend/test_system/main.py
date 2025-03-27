from abc import ABC, abstractmethod
from typing import List, Type

from pydantic import BaseModel

from database import get_db
from database.models import User, WordTranslation, Word

from .caching import CachingInterface


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


class NoQuestionsException(Exception):
    pass


class Test:
    _questions = []
    _current_question = 0
    _user: User

    def __init__(self, user: User, questions: List[QuestionInterface],
                 caching_class: Type[CachingInterface] | None = None):
        self._questions = questions
        self._user = user
        self._current_question = 0
        if caching_class is None:
            self._caching = None
        else:
            self._caching = caching_class(f"test:user:{user.id}", self)
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
        instance: Test = caching_class.load(f"test:user:{user.id}")
        return instance
