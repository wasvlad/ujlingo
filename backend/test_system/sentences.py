import random
from typing import List

from database import get_db
from database.models import SentenceTranslation, Sentence, User, SentenceTranslationKnowledge as TranslationKnowledge
from .main import Result, QuestionJsonBase, QuestionInterface, QuestionTypeEnum, KnowledgeSaverInterface


class TranslationQuestion(QuestionInterface):
    _translation: SentenceTranslation

    def __init__(self, translation: SentenceTranslation):
        self._translation = translation

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
    type: int = QuestionTypeEnum.reorder.value

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

class TranslationKnowledgeSaver(KnowledgeSaverInterface):
    def __init__(self, user: User, translation: SentenceTranslation):
        self._user_id = user.id
        self._translation_id = translation.id
        self._difference = 0

    def answered(self, result: Result):
        db = next(get_db())
        knowledge = db.query(TranslationKnowledge).filter(
            TranslationKnowledge.user_id == self._user_id,
            TranslationKnowledge.sentence_translation_id == self._translation_id
        ).first()
        if not knowledge:
            knowledge = TranslationKnowledge(user_id=self._user_id, sentence_translation_id=self._translation_id)
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

    def asked(self):
        db = next(get_db())
        knowledge = db.query(TranslationKnowledge).filter(
            TranslationKnowledge.user_id == self._user_id,
            TranslationKnowledge.sentence_translation_id == self._translation_id
        ).first()
        if not knowledge:
            knowledge = TranslationKnowledge(user_id=self._user_id, sentence_translation_id=self._translation_id)
            self._difference = 0
            db.add(knowledge)
        else:
            was = knowledge.knowledge
            knowledge.knowledge -= 25
            knowledge.knowledge = min(100, knowledge.knowledge)
            knowledge.knowledge = max(0, knowledge.knowledge)
            self._difference = was - knowledge.knowledge
        db.commit()
