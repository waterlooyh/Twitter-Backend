from django.contrib.auth.models import User
from django.test import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now

# Create your tests here.
class TweetTests(TestCase):

    def test_hours_to_now(self):
        hangbao = User.objects.create_user(username='hangbao')
        tweet = Tweet.objects.create(user=hangbao, content='hangbao is good!')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
