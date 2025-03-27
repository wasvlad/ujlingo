from typing import Type

from sqlalchemy import func

from ..main import Test, WordsTranslationQuestion
from database.models import WordTranslation, User
from database import get_db
from ..caching import CachingInterface


class WordTranslationsTestBuilder:
    @staticmethod
    def build(user: User, number:int = 10, caching_class: Type[CachingInterface] | None = None) -> Test:
        questions = []
        db = next(get_db())
        for i in range(number):
            translation = db.query(WordTranslation).order_by(func.random()).first()
            question = WordsTranslationQuestion(translation)
            questions.append(question)
        test = Test(user, questions, caching_class)
        return test