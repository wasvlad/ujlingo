from sqlalchemy import func

from ..main import QuestionInterface, Result, QuestionJsonBase, Test
from database.models import WordTranslation, User
from database import get_db


class WordsTranslationQuestion(QuestionInterface):
    _word_translation: WordTranslation

    def __init__(self, translation: WordTranslation):
        self._word_translation = translation
        self._word_translation.word_original = translation.word_original
        self._word_translation.word_translated = translation.word_translated

    def give_answer(self, answer: str) -> Result:
        is_correct = answer == self._word_translation.word_translated.word
        result = Result(is_correct=is_correct, correct_answer=self._word_translation.word_translated.word)
        return result

    def get(self) -> QuestionJsonBase:
        result = QuestionJsonBase(question="Translate the word: " + self._word_translation.word_original.word)
        return result


class WordTranslationsTestBuilder:
    @staticmethod
    def build(user: User, number:int = 10) -> Test:
        questions = []
        for i in range(number):
            db = next(get_db())
            translation = db.query(WordTranslation).order_by(func.random()).first()
            question = WordsTranslationQuestion(translation)
            questions.append(question)
        test = Test(user, questions)
        return test