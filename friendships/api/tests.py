from rest_framework.test import APIClient
from testing.testcases import TestCase
from friendships.models import Friendship

FOLLOWERS_API = '/api/friendships/{}/followers/'
FOLLOWINGS_API = '/api/friendships/{}/followings/'
FOLLOW_API = '/api/friendships/{}/follow/'
UNFOLLOW_API = '/api/friendships/{}/unfollow/'

class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()
        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)
        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        for i in range(2):
            follower = self.create_user('user2_follower{}'.format(i), 'user2_follower{}@jiuzhang.com'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        for i in range(3):
            following = self.create_user('user2_following{}'.format(i), 'user2_following{}@jiuzhang.com'.format(i))
            Friendship.objects.create(from_user=self.user2, to_user=following)

    def test_follow_api(self):
        url = FOLLOW_API.format(self.user2.id)
        # must log in
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # get method
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 405)

        # cannot follow myself
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 201)
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        count = Friendship.objects.count()
        response = self.user2_client.post(FOLLOW_API.format(self.user1.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow_api(self):
        url = UNFOLLOW_API.format(self.user2.id)
        # must log in
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # get method
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 405)

        # cannot unfollow myself
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 400)

        response = self.user1_client.post(FOLLOW_API.format(self.user2.id))
        self.assertEqual(response.status_code, 201)
        count = Friendship.objects.count()
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Friendship.objects.count(), count - 1)

        count = Friendship.objects.count()
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followers_api(self):
        url = FOLLOWERS_API.format(self.user2.id)
        # post method
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(response.data['followers'][0]['user']['username'], 'user2_follower1')
        self.assertEqual(response.data['followers'][1]['user']['username'], 'user2_follower0')

    def test_followings_api(self):
        url = FOLLOWINGS_API.format(self.user2.id)
        # post method
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(response.data['followings'][0]['user']['username'], 'user2_following2')
        self.assertEqual(response.data['followings'][1]['user']['username'], 'user2_following1')
        self.assertEqual(response.data['followings'][2]['user']['username'], 'user2_following0')
