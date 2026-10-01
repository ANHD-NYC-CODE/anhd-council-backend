from rest_framework_simplejwt.tokens import RefreshToken


def issue_jwt_pair_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
