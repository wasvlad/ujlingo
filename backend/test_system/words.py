from random import shuffle
from typing import List

from database import get_db
from database.models import WordTranslation, Word, User, WordTranslationKnowledge as TranslationKnowledge
from .main import Result, QuestionJsonBase, QuestionInterface, KnowledgeSaverInterface, QuestionTypeEnum


class MSQQuestionJson(QuestionJsonBase):
    options: List[str]
    type: int = QuestionTypeEnum.msq.value

class TranslationQuestion(QuestionInterface):
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


class LanguageException(Exception):
    pass


class MSQQuestion(TranslationQuestion):
    def __init__(self, translation: WordTranslation, options: List[Word | str] = None):
        super().__init__(translation)
        if options is None:
            options = []
        self._possible_answers: List[str] = []
        for word in options:
            if isinstance(word, str):
                self._possible_answers.append(word)
                continue
            elif not isinstance(word, Word):
                raise TypeError("Options should be str or Word")
            if word.language != translation.word_translated.language:
                raise LanguageException("Options language should be as language of translated word")
            self._possible_answers.append(word.word)
        if not translation.word_translated.word in self._possible_answers:
            self._possible_answers.append(translation.word_translated.word)
        shuffle(self._possible_answers)

    def get(self) -> MSQQuestionJson:
        result_p = super().get()
        options = [word for word in self._possible_answers]
        result = MSQQuestionJson(question=result_p.question, options=options)
        return result


class QuestionNotAskedException(Exception):
    pass

class TranslationKnowledgeSaver(KnowledgeSaverInterface):
    def __init__(self, user: User, word_translation: WordTranslation):
        self._user_id = user.id
        self._word_translation_id = word_translation.id
        self._asked = False
        self._difference = 0

    def answered(self, result: Result):
        db = next(get_db())
        knowledge = db.query(TranslationKnowledge).filter(
            TranslationKnowledge.user_id == self._user_id,
            TranslationKnowledge.word_translation_id == self._word_translation_id
        ).first()
        if not knowledge:
            knowledge = TranslationKnowledge(user_id=self._user_id, word_translation_id=self._word_translation_id)
            knowledge.knowledge = 0
            db.add(knowledge)
        knowledge.knowledge += self._difference
        if result.is_correct:
            knowledge.knowledge += 20
        else:
            knowledge.knowledge -= 50
        knowledge.knowledge = min(100, knowledge.knowledge)
        knowledge.knowledge = max(0, knowledge.knowledge)
        db.commit()
        self._asked = False

    def asked(self):
        db = next(get_db())
        knowledge = db.query(TranslationKnowledge).filter(
            TranslationKnowledge.user_id == self._user_id,
            TranslationKnowledge.word_translation_id == self._word_translation_id
        ).first()
        if not knowledge:
            knowledge = TranslationKnowledge(user_id=self._user_id, word_translation_id=self._word_translation_id)
            self._difference = 0
            db.add(knowledge)
        else:
            was = knowledge.knowledge
            knowledge.knowledge -= 25
            knowledge.knowledge = min(100, knowledge.knowledge)
            knowledge.knowledge = max(0, knowledge.knowledge)
            self._difference = was - knowledge.knowledge
        db.commit()
