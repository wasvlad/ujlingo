from random import randint

from typing import Type

from database.models import User
from test_system.caching import CachingInterface
from test_system.main import Test, QuestionProxy
from test_system.builder.question import get_new_translations, build_msq_question
from test_system.words import TranslationKnowledgeSaver, TranslationQuestion


class NewWordsTestBuilder:
    @staticmethod
    def build(user: User, number: int = 10, caching_class: Type[CachingInterface] | None = None) -> Test:
        questions = []
        translations = get_new_translations(number, 10)
        for translation in translations:
            if randint(0, 1) == 0:
                question = build_msq_question(translation)
            else:
                question = TranslationQuestion(translation)
            question = QuestionProxy(question, TranslationKnowledgeSaver(user, translation))
            questions.append(question)
        test = Test(user, questions, caching_class)
        return test
