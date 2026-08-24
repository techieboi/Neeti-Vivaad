from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from core.models import User
from debate.models import DebateSession


class CustomDebateTopicApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='debater', password='secret')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @patch(
        'debate.views.generate_agent_argument',
        return_value=('A grounded policy argument.', 'Grounded in [TEST-DOC]', 'TEST-DOC')
    )
    @patch(
        'debate.views.MoSPIRAGStore.retrieve',
        return_value=[{
            'doc_code': 'TEST-DOC',
            'title': 'Test Policy Document',
            'content': 'A reference passage for the debate.'
        }]
    )
    def test_starts_debate_with_custom_topic(self, _retrieve, _generate_argument):
        topic = 'Should public agencies publish AI impact assessments?'

        response = self.client.post(
            '/api/debate/start/',
            {'custom_topic': topic},
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['scenario_title'], topic)
        self.assertEqual(response.data['category'], 'Custom Topic')
        self.assertEqual(response.data['active_constraint'], 'Open deliberation with no preset constraint.')

        session = DebateSession.objects.get(id=response.data['session_id'])
        self.assertEqual(session.scenario.title, topic)
        self.assertEqual(session.scenario.status, 'Draft')

        scenario_list = self.client.get('/api/debate/scenarios/')
        listed_ids = [scenario['id'] for scenario in scenario_list.data['scenarios']]
        self.assertNotIn(session.scenario_id, listed_ids)

    def test_rejects_blank_custom_topic(self):
        response = self.client.post(
            '/api/debate/start/',
            {'custom_topic': '   '},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Enter a custom debate topic.')
        self.assertFalse(DebateSession.objects.exists())
