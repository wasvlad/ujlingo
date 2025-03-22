# import pytest
# from endpoints.admin.data_migration import words_translations_to_pairs
# from fastapi.testclient import TestClient
# from unittest.mock import patch, AsyncMock, Mock
# from main import app
# from database.models import (User, Base, WordUa, WordTranslation, WordEn,
#                              LastWordTranslationRequest as LastRequest, WordTranslationKnowledge as Knowledge)
# from database import get_db, DatabaseSession, engine
# from endpoints.user.tools import validate_session
#
# # Mock dependencies
# def override_validate_session():
#     return User(id=1, is_admin=False, email="test@example.com")
#
# def override_get_db():
#     return AsyncMock()
#
# class TestGetRandomWord:
#     def setup_class(self):
#         self.session = DatabaseSession()
#
#     @pytest.fixture
#     def client(self):
#         app.dependency_overrides[get_db] = self.override_get_db
#         app.dependency_overrides[validate_session] = override_validate_session
#         return TestClient(app)
#
#     @staticmethod
#     def setup_method():
#         Base.metadata.drop_all(engine)
#         Base.metadata.create_all(engine)
#         db = next(get_db())
#         db.add(User(email="test@example.com", name="Test", surname="User", password_hash="hashed_password", id=1))
#         word_ua = WordUa(word="привіт")
#         word_en = WordEn(word="hello")
#         db.add_all([word_ua, word_en])
#         db.commit()
#         word_translation = WordTranslation(word_ua_id=word_ua.id, word_en_id=word_en.id)
#         db.add(word_translation)
#         db.commit()
#
#     def override_get_db(self):
#         return self.session
#
#     def teardown_class(self):
#         self.session.close()
#
#     @pytest.mark.asyncio
#     async def test_get_random_word(self, client):
#         response = client.get("/teaching/random-word?translate_from=en", headers={"access-token": "access-token"})
#         assert response.status_code == 200
#         assert response.json() == {"word": "hello"}
#         db = next(get_db())
#         last_request = db.query(LastRequest).all()
#         assert len(last_request) == 1
#         last_request = last_request[0]
#         assert last_request.user_id == 1
#         assert last_request.knowledge_id == 1
#
# class TestValidateWordTranslation:
#     def setup_class(self):
#         self.session = DatabaseSession()
#
#     @pytest.fixture
#     def client(self):
#         app.dependency_overrides[get_db] = self.override_get_db
#         app.dependency_overrides[validate_session] = override_validate_session
#         return TestClient(app)
#
#     @staticmethod
#     def setup_method():
#         Base.metadata.drop_all(engine)
#         Base.metadata.create_all(engine)
#         db = next(get_db())
#         db.add(User(email="test@example.com", name="Test", surname="User", password_hash="hashed_password", id=1))
#         word_ua = WordUa(word="привіт")
#         word_en = WordEn(word="hello")
#         db.add_all([word_ua, word_en])
#         db.commit()
#         word_translation = WordTranslation(word_ua_id=word_ua.id, word_en_id=word_en.id)
#         db.add(word_translation)
#         db.commit()
#
#     def override_get_db(self):
#         return self.session
#
#     def teardown_class(self):
#         self.session.close()
#
#     @pytest.mark.asyncio
#     async def test_validate_word_correct(self, client):
#         client.get("/teaching/random-word?translate_from=en", headers={"access-token": "access-token"})
#         response = client.post("/teaching/random-word", json={
#             "translate_from": "en",
#             "word_original": "hello",
#             "word_translated": "привіт"
#         })
#         assert response.status_code == 200
#         assert response.json() == {"is_correct": True, "possible_answers": ["привіт"]}
#         db = next(get_db())
#         last_request = db.query(LastRequest).all()
#         assert len(last_request) == 0
#         knowledge = db.query(Knowledge).all()[0]
#         assert knowledge.knowledge == 20
#
#     @pytest.mark.asyncio
#     async def test_validate_word_wrong(self, client):
#         client.get("/teaching/random-word?translate_from=en", headers={"access-token": "access-token"})
#         response = client.post("/teaching/random-word", json={
#             "translate_from": "en",
#             "word_original": "hello",
#             "word_translated": "бувай"
#         })
#         assert response.status_code == 200
#         assert response.json() == {"is_correct": False, "possible_answers": ["привіт"]}
#         db = next(get_db())
#         last_request = db.query(LastRequest).all()
#         assert len(last_request) == 0
#         knowledge = db.query(Knowledge).all()[0]
#         assert knowledge.knowledge == 0
