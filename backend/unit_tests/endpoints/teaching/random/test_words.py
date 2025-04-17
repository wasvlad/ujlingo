# import logging
#
# import pytest
# from fastapi.testclient import TestClient
#
# from test_system.caching import RedisCaching, RedisCachingException
# from endpoints.user.tools import validate_session
# from main import app
# from database.models import User, Word, WordTranslation
# from database import get_db
# from test_system.main import Test
# from unit_tests.tools import clear_database, add_word_translation
#
# # Mock dependencies
# def override_validate_user_session():
#     return User(id=1, is_admin=False)
#
# class TestWordsTesting:
#
#     @pytest.fixture
#     def client(self):
#         app.dependency_overrides[validate_session] = override_validate_user_session
#         return TestClient(app)
#
#     def setup_method(self):
#         logging.basicConfig(level=logging.INFO)
#         clear_database()
#         self.db = next(get_db())
#         self.word_translation = WordTranslation()
#         self.word_original = Word(word="привіт", language="ua")
#         self.word_translated = Word(word="hi", language="en")
#         user = User(email="email@email.com", name="Test", surname="User", password_hash="password")
#         self.db.add(user)
#         add_word_translation(db=self.db, word_original=self.word_original, word_translated=self.word_translated,
#                              word_translation=self.word_translation)
#
#     def teardown_method(self):
#         try:
#             user = override_validate_user_session()
#             test = Test.load_from_cache(user, caching_class=RedisCaching)
#             test.delete()
#         except RedisCachingException:
#             # Ok, nothing to delete
#             pass
#
#     def teardown_class(self):
#         app.dependency_overrides.clear()
#
#     @pytest.mark.asyncio
#     async def test_normal_flow(self, client):
#         result = client.post("/teaching/random/words/init_test")
#         assert result.status_code == 200
#         assert result.json() == {"message": "Test session initialized"}
#         for i in range(10):
#             result = client.get("/teaching/test/get_question")
#             assert result.status_code == 200
#             assert result.json().get("question", None) is not None
#             logging.info("Got question: " + result.json().get("question"))
#             result = client.post("/teaching/test/answer_question",
#                                  json={"answer": self.word_translated.word})
#             assert result.status_code == 200
#             assert result.json().get("is_correct") is True
#         result = client.get("/teaching/test/get_question")
#         assert result.status_code == 200
#         assert result.json().get("message", None) is not None
#         result = client.post("/teaching/test/answer_question",
#                              json={"answer": self.word_translated.word})
#         assert result.status_code == 400
#         assert result.json() == {"detail": "Test session is not initialized"}
#
#
#     @pytest.mark.asyncio
#     async def test_already_initialized(self, client):
#         result = client.post("/teaching/random/words/init_test")
#         assert result.status_code == 200
#         assert result.json() == {"message": "Test session initialized"}
#         result = client.post("/teaching/random/words/init_test")
#         assert result.status_code == 400
#         assert result.json() == {"detail": "Test session is already initialized"}
#
#     def test_not_initialized(self, client):
#         result = client.get("/teaching/test/get_question")
#         assert result.status_code == 400
#         assert result.json() == {"detail": "Test session is not initialized"}
#         result = client.post("/teaching/test/answer_question",
#                              json={"answer": self.word_translated.word})
#         assert result.status_code == 400
#         assert result.json() == {"detail": "Test session is not initialized"}
#
#     def test_is_finished(self, client):
#         result = client.post("/teaching/random/words/init_test")
#         assert result.status_code == 200
#         assert result.json() == {"message": "Test session initialized"}
#         for i in range(10):
#             result = client.post("/teaching/test/answer_question",
#                                  json={"answer": "wrong"})
#             assert result.status_code == 200
#             assert result.json().get("is_correct") is False
#         result = client.post("/teaching/test/answer_question",
#                              json={"answer": self.word_translated.word})
#         assert result.status_code == 400
#         assert result.json() == {"detail": "Test is finished"}
