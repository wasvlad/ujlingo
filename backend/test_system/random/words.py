from sqlalchemy import func

from ..main import QuestionInterface, Result, QuestionJsonBase, Test
from database.models import WordTranslation, User, Word
from database import get_db


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


class WordTranslationsTestBuilder:
    @staticmethod
    def build(user: User, number:int = 10) -> Test:
        questions = []
        db = next(get_db())
        for i in range(number):
            translation = db.query(WordTranslation).order_by(func.random()).first()
            question = WordsTranslationQuestion(translation)
            questions.append(question)
        test = Test(user, questions)
        return test