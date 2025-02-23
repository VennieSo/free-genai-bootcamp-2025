import unittest
import json
from app import create_app

class StudySessionAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

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

if __name__ == '__main__':
    unittest.main()