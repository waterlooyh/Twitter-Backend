from friendships.api.serializers import (
    FollowerSerializer, 
    FollowingSerializer,
    FriendshipCreateSerializer,
)
from django.contrib.auth.models import User
from friendships.models import Friendship
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

class FriendshipViewSet(viewsets.GenericViewSet):
    # GET /api/friendship/{}/followers/
    # GET /api/friendship/{}/followings/
    # POST /api/friendship/{}/follow/
    # POST /api/friendship/{}/unfollow/
    queryset = User.objects.all()

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response({'followers': serializer.data}, 200)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response({'followings': serializer.data}, 200)
    
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        if Friendship.objects.filter(
                from_user_id=request.user.id, 
                to_user_id=pk,
        ).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, 201)
        serializer = FriendshipCreateSerializer(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=400)
        serializer.save()
        return Response({'success': True}, status=201)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=400)
        deleted, _ = Friendship.objects.filter(
            from_user_id=request.user.id, 
            to_user_id=pk,
        ).delete()
        return Response({'success': True, 'deleted': deleted}, status=200)
