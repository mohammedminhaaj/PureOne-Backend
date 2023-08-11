from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from common.serializers.user_serializer import UserLocationSerializer
from common import constants
from ..models import UserLocation


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_edit_user_location(request: Request, user_location_id: str | None = None):
    if user_location_id:
        try:
            user_location = UserLocation.objects.get(
                pk=user_location_id, user=request.user)
            serializer = UserLocationSerializer(
                data=request.data, instance=user_location)
        except UserLocation.DoesNotExist:
            return Response(data={"details": "User location does not exists"}, status=status.HTTP_404_NOT_FOUND)
    else:
        serializer = UserLocationSerializer(data=request.data)
    if serializer.is_valid():
        user_location = serializer.save(user=request.user)
        return Response(data={"details": f"location {'added' if not user_location_id else 'updated'} successfully", "user_location": serializer.data}, status=status.HTTP_201_CREATED)
    else:
        return Response(data={"details": constants.FORM_ERROR, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_user_location(request: Request, user_location_id: str | None = None):
    try:
        UserLocation.objects.get(
            user=request.user, pk=user_location_id).delete()
    except UserLocation.DoesNotExist:
        pass
    except Exception:
        return Response(data={"details": constants.SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(data={"details": "location removed successfully."}, status=status.HTTP_200_OK)
