from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, orm
from sqlalchemy.orm import declarative_base, relationship, validates

DeclarativeBase = declarative_base()


class Base(DeclarativeBase):
    __abstract__ = True  # does not affect subclasses

    id = Column(Integer, primary_key=True, autoincrement=True)


class User(Base):
    __tablename__ = "my_user"  # changed to my_user to avoid conflict with the built-in User model

    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    is_confirmed = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)


class Session(Base):
    __tablename__ = "session"

    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('my_user.id', ondelete='CASCADE'), nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship(User)


class Word(Base):
    __tablename__ = "word"

    word = Column(String, unique=True, nullable=False)
    language = Column(String, nullable=False)


class WordTranslation(Base):
    __tablename__ = "word_translation"

    word_original_id = Column(Integer, ForeignKey('word.id', ondelete='CASCADE'), nullable=False)
    word_translated_id = Column(Integer, ForeignKey('word.id', ondelete='CASCADE'), nullable=False)

    word_original = relationship('Word', foreign_keys=[word_original_id])
    word_translated = relationship('Word', foreign_keys=[word_translated_id])


class WordTranslationKnowledge(Base):
    __tablename__ = "word_translation_knowledge"

    user_id = Column(Integer, ForeignKey('my_user.id', ondelete='CASCADE'), nullable=False)
    word_translation_id = Column(Integer, ForeignKey('word_translation.id', ondelete='CASCADE'), nullable=False)
    knowledge = Column(Integer, nullable=False, default=0)

    user = relationship(User)
    word_translation = relationship(WordTranslation)
