from rest_framework.test import APIClient
from testing.testcases import TestCase
from newsfeeds.models import NewsFeed

NEWSFEED_LIST_API = '/api/newsfeeds/'
FOLLOW_API = '/api/friendships/{}/follow/'
TWEET_CREATE_API = '/api/tweets/'

class NewsFeedApiTests(TestCase):
    
    def setUp(self):
        self.anonymous_client = APIClient()
        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_list_api(self):
        # must log in
        response = self.anonymous_client.post(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 403)

        # post method
        response = self.user2_client.post(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 405)

        # have 0 newsfeed at first
        response = self.user2_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # user2_client follow user1
        url = FOLLOW_API.format(self.user1.id)
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 201)
        # user1 post a tweet
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'hangbao is the best'
        })
        posted_tweet_id = response.data['id']
        self.assertEqual(response.status_code, 201)
        response = self.user2_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)
        # user2 post a tweet
        response = self.user2_client.post(TWEET_CREATE_API, {
            'content': 'hangbao is the best yyds'
        })
        self.assertEqual(response.status_code, 201)
        response = self.user2_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 2)
