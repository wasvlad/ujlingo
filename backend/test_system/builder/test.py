from random import randint

from typing import Type

from fastapi import HTTPException

from database.models import User
from test_system.caching import CachingInterface
from test_system.main import Test, QuestionProxy, QuestionInterface
from test_system.builder.question import get_new_word_translations, build_msq_question, \
    get_word_translations_weak_knowledge, \
    get_word_translations_strong_knowledge, get_new_sentence_translations, \
    get_sentence_translations_weak_knowledge, get_sentence_translations_strong_knowledge
from test_system.words import TranslationKnowledgeSaver, TranslationQuestion
import test_system.sentences as sentences


class TestBuilder:
    def __init__(self, user: User):
        self.__questions = []
        self.__user = user

    def add_new_words(self, number: int = 10) -> None:
        translations = get_new_word_translations(number)
        for translation in translations:
            if randint(0, 1) == 0:
                question = build_msq_question(translation)
            else:
                question = TranslationQuestion(translation)
            question = QuestionProxy(question, TranslationKnowledgeSaver(self.__user, translation))
            self.__questions.append(question)

    def add_weak_knowledge_words(self, number: int = 10) -> None:
        translations = get_word_translations_weak_knowledge(number)
        for translation in translations:
            if randint(0, 1) == 0:
                question = build_msq_question(translation)
            else:
                question = TranslationQuestion(translation)
            question = QuestionProxy(question, TranslationKnowledgeSaver(self.__user, translation))
            self.__questions.append(question)

    def add_strong_knowledge_words(self, number: int = 10) -> None:
        translations = get_word_translations_strong_knowledge(number)
        for translation in translations:
            if randint(0, 1) == 0:
                question = build_msq_question(translation)
            else:
                question = TranslationQuestion(translation)
            question = QuestionProxy(question, TranslationKnowledgeSaver(self.__user, translation))
            self.__questions.append(question)

    def add_new_sentences(self, number: int = 10) -> None:
        translations = get_new_sentence_translations(number)
        for translation in translations:
            if randint(0, 1) == 0:
                question = sentences.ReorderTranslationQuestion(translation)
            else:
                question = sentences.TranslationQuestion(translation)
            question = QuestionProxy(question, sentences.TranslationKnowledgeSaver(self.__user, translation))
            self.__questions.append(question)

    def add_weak_sentences(self, number: int = 10) -> None:
        translations = get_sentence_translations_weak_knowledge(number)
        for translation in translations:
            if randint(0, 1) == 0:
                question = sentences.ReorderTranslationQuestion(translation)
            else:
                question = sentences.TranslationQuestion(translation)
            question = QuestionProxy(question, sentences.TranslationKnowledgeSaver(self.__user, translation))
            self.__questions.append(question)

    def add_strong_knowledge_sentences(self, number: int = 10) -> None:
        translations = get_sentence_translations_strong_knowledge(number)
        for translation in translations:
            if randint(0, 1) == 0:
                question = sentences.ReorderTranslationQuestion(translation)
            else:
                question = sentences.TranslationQuestion(translation)
            question = QuestionProxy(question, sentences.TranslationKnowledgeSaver(self.__user, translation))
            self.__questions.append(question)

    def add_custom(self, question: QuestionProxy | QuestionInterface):
        self.__questions.append(question)

    def build(self, caching_class: Type[CachingInterface] | None = None) -> Test:
        if len(self.__questions) == 0:
            raise HTTPException(status_code=400, detail="No questions")
        test = Test(self.__user, self.__questions, caching_class)
        return test
