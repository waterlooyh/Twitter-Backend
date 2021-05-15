from newsfeeds.models import NewsFeed
from rest_framework import serializers
from tweets.api.serializers import TweetSerializer
from accounts.api.serializers import UserSerializer

class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'user', 'tweet',)
