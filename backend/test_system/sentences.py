import random
from typing import List

from database import get_db
from database.models import SentenceTranslation, Sentence
from .main import Result, QuestionJsonBase, QuestionInterface


class TranslationQuestion(QuestionInterface):
    _translation: SentenceTranslation

    def __init__(self, translation: SentenceTranslation):
        self._translation = translation
        self._translation.sentence_original = self._translation.sentence_original
        self._translation.sentence_translated = self._translation.sentence_translated

    def give_answer(self, answer: str) -> Result:
        db = next(get_db())
        sentence = db.query(Sentence).filter(Sentence.sentence == answer).first()
        if sentence is None:
            result = Result(is_correct=False, correct_answer=self._translation.sentence_translated.sentence)
            return result
        original_id = self._translation.sentence_original_id
        translation = db.query(SentenceTranslation).filter(SentenceTranslation.sentence_original_id == original_id,
                                                           SentenceTranslation.sentence_translated_id == sentence.id).first()
        if translation is None:
            result = Result(is_correct=False, correct_answer=self._translation.sentence_translated.sentence)
            return result
        is_correct = True
        result = Result(is_correct=is_correct, correct_answer=self._translation.sentence_translated.sentence)
        return result

    def get(self) -> QuestionJsonBase:
        result = QuestionJsonBase(question="Translate the sentence: " + self._translation.sentence_original.sentence)
        return result

class ReorderQuestionJson(QuestionJsonBase):
    tokens: List[str]
    type: int = 2

class ReorderTranslationQuestion(TranslationQuestion):
    def __init__(self, translation: SentenceTranslation):
        super().__init__(translation)
        translated = translation.sentence_translated
        words = translated.sentence.split(' ')
        for i in range(len(words)):
            last_symbol = words[i][-1]
            if last_symbol in [',', '.', '!', '?']:
                words[i] = words[i][:-1]
                words.append(last_symbol)
        random.shuffle(words)
        self._tokens = words


    def get(self) -> ReorderQuestionJson:
        result_p = super().get()
        result = ReorderQuestionJson(question=result_p.question, tokens=self._tokens)
        return result