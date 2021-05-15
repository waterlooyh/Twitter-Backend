from friendships.models import Friendship
from django.contrib.auth.models import User

class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(to_user=user)
        followers_id = [friendship.from_user_id for friendship in friendships]
        return User.objects.filter(id__in=follower_ids)
