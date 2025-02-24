import unittest
import json
from app import create_app

class StudySessionAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Create a study session for testing
        self.client.post('/api/study-sessions', 
                         data=json.dumps({"group_id": 1, "study_activity_id": 1}),
                         content_type='application/json')

    def test_create_study_session_valid(self):
        response = self.client.post('/api/study-sessions', 
                                     data=json.dumps({"group_id": 1, "study_activity_id": 1}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('session_id', response.get_json())

    def test_missing_group_id(self):
        response = self.client.post('/api/study-sessions', 
                                     data=json.dumps({"study_activity_id": 1}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "group_id is required"})

    def test_missing_study_activity_id(self):
        response = self.client.post('/api/study-sessions', 
                                     data=json.dumps({"group_id": 1}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "study_activity_id is required"})

    def test_non_existent_group_id(self):
        response = self.client.post('/api/study-sessions', 
                                     data=json.dumps({"group_id": 999, "study_activity_id": 1}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "group_id does not exist"})

    def test_non_existent_study_activity_id(self):
        response = self.client.post('/api/study-sessions', 
                                     data=json.dumps({"group_id": 1, "study_activity_id": 999}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "study_activity_id does not exist"})

    def test_database_integrity_error(self):
        # This test would require setting up a scenario where an integrity error occurs.
        # For example, you could try to insert a session with a group_id that violates a constraint.
        pass  # Implement this test based on your database setup.

    def test_submit_word_reviews_valid(self):
        # Assuming the session ID is 1
        response = self.client.post('/api/study-sessions/1/review', 
                                     data=json.dumps({
                                         "word_reviews": [
                                             {"word_id": 1, "correct": True},
                                             {"word_id": 2, "correct": False}
                                         ]
                                     }),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["message"], "Word reviews submitted successfully")

    def test_invalid_session_id(self):
        response = self.client.post('/api/study-sessions/999/review', 
                                     data=json.dumps({
                                         "word_reviews": [
                                             {"word_id": 1, "correct": True}
                                         ]
                                     }),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Study session not found"})

    def test_empty_word_reviews(self):
        response = self.client.post('/api/study-sessions/1/review', 
                                     data=json.dumps({"word_reviews": []}),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Word reviews must be a non-empty array"})

    def test_invalid_review_object(self):
        response = self.client.post('/api/study-sessions/1/review', 
                                     data=json.dumps({
                                         "word_reviews": ["not an object"]
                                     }),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Each review must be an object"})

    def test_invalid_word_id(self):
        response = self.client.post('/api/study-sessions/1/review', 
                                     data=json.dumps({
                                         "word_reviews": [
                                             {"word_id": "invalid", "correct": True}
                                         ]
                                     }),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "word_id must be a valid integer"})

    def test_non_existent_word_id(self):
        response = self.client.post('/api/study-sessions/1/review', 
                                     data=json.dumps({
                                         "word_reviews": [
                                             {"word_id": 999, "correct": True}
                                         ]
                                     }),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "word_id 999 does not exist"})

    def test_invalid_correct_value(self):
        response = self.client.post('/api/study-sessions/1/review', 
                                     data=json.dumps({
                                         "word_reviews": [
                                             {"word_id": 1, "correct": "not a boolean"}
                                         ]
                                     }),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "correct must be a boolean value"})

if __name__ == '__main__':
    unittest.main()