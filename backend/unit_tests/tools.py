from database import engine, DatabaseSession
from database.models import Base, Word, WordTranslation


def clear_database():
    DatabaseSession.close_all()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def add_word_translation(db: DatabaseSession, word_original: Word, word_translated: Word, 
                         word_translation: WordTranslation) -> None:
    db.add(word_original)
    db.add(word_translated)
    db.commit()
    word_translation.word_original_id = word_original.id
    word_translation.word_translated_id = word_translated.id
    db.add(word_translation)
    db.commit()