from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from .models import Submission, MachineGenCodeDetectionResult

User = get_user_model()


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['programming_language_id', 'content']

    content = serializers.CharField(max_length=100000, required=True)
    # programming_language_id = serializers.IntegerField(min_value=1, required=True)


class MachineGenCodeDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineGenCodeDetectionResult
        fields = '__all__'


class SubmissionDetailSerializer(serializers.ModelSerializer):
    machine_gen_code_detection_result = MachineGenCodeDetectionSerializer(read_only=True, many=True)

    class Meta:
        model = Submission
        fields = [
            'id',
            'name',
            'user_id',
            'programming_language_id',
            'coding_problem_id',
            'machine_gen_detection_status',
            'code_execution_status',
            'code_similarity_detection_status',
            'vulnerability_detection_status',
            'created_at',
            'updated_at',
            'machine_gen_code_detection_result'
        ]


class PaginationSerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1)
    per_page = serializers.IntegerField(default=10)

    class Meta:
        fields = ['page', 'per_page']


class SortSerializer(serializers.Serializer):
    SORT_ORDERS = ['ASC', 'DESC']
    sort_order = serializers.ChoiceField(choices=SORT_ORDERS, default=SORT_ORDERS[0])

    class Meta:
        fields = ['sort_order']


class SubmissionListSerializer(PaginationSerializer, SortSerializer):
    SORT_BY_FIELDS = [
        'id',
        'created_at',
        'programming_language_id'
    ]
    sort_by = serializers.ChoiceField(choices=SORT_BY_FIELDS, default=SORT_BY_FIELDS[0])
    programming_language_id = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        fields = ['page', 'per_page', 'sort_by', 'sort_order', 'programming_language_id']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, required=True)
    password = serializers.CharField(allow_null=False, required=True)

    class Meta:
        fields = ['email', 'password']


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(allow_null=False, required=True)
    firstname = serializers.CharField(allow_null=False, required=True)
    lastname = serializers.CharField(allow_null=False, required=True)
    password = serializers.CharField(allow_null=False, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(allow_null=False, required=True, validators=[validate_password])

    class Meta:
        fields = ['email', 'username', 'firstname', 'firstname', 'password']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
