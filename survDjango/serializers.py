# serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationUserSerializer(serializers.ModelSerializer):
    """
    ModelSerializer로 만든다.
    """

    # password2는 따로 없기 때문에 추가로 만들어 주어야 한다.
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        """
        메타 클래스에 필드, 모델 등을 설정하고
        password 필드의 스타일을 정해준다.
        """
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        """
        저장시 한 번 더 확인한다.
        """
        account = User(
            email=self.validated_data['email'],
            username=self.validated_data['username']
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        account.set_password(password)
        account.save()
        return account
