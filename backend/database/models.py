from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    is_confirmed = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)


class Session(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    is_active = Column(Boolean, default=True)


class WordUa(Base):
    __tablename__ = "word_ua"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, unique=True, nullable=False)


class WordEn(Base):
    __tablename__ = "word_en"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, unique=True, nullable=False)


class WordTranslation(Base):
    __tablename__ = "word_translation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word_ua_id = Column(Integer, ForeignKey('word_ua.id', ondelete='CASCADE'), nullable=False)
    word_en_id = Column(Integer, ForeignKey('word_en.id', ondelete='CASCADE'), nullable=False)

    word_en = relationship('WordEn')
    word_ua = relationship('WordUa')


class WordTranslationKnowledge(Base):
    __tablename__ = "word_translation_knowledge"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    word_translation_id = Column(Integer, ForeignKey('word_translation.id', ondelete='CASCADE'), nullable=False)
    knowledge = Column(Integer, nullable=False, default=0)

    word_translation = relationship('WordTranslation')
    user = relationship('User')


class LastWordTranslationRequest(Base):
    __tablename__ = "last_word_translation_request"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True)
    knowledge_id = Column(Integer,
                          ForeignKey('word_translation_knowledge.id', ondelete='CASCADE'),
                          nullable=False)

    knowledge = relationship('WordTranslationKnowledge')
    user = relationship('User')