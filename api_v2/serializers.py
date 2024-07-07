from rest_framework import serializers
from .models import Submission, MachineGenCodeDetectionResult


class MachineGenCodeDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineGenCodeDetectionResult
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    machine_gen_code_detection_result = MachineGenCodeDetectionSerializer(read_only=True, many=True)

    class Meta:
        model = Submission
        fields = [
            'id',
            'name',
            'user_id',
            'filepath',
            'programming_language_id',
            'coding_problem_id',
            'machine_gen_detection_status',
            'code_execution_status',
            'code_similarity_detection_status',
            'vulnerability_detection_status',
            'created_at',
            'updated_at',
            'machine_gen_code_detection_result',
        ]


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['programming_language_id', 'content']

    content = serializers.CharField(max_length=100000, required=True)
    # programming_language_id = serializers.IntegerField(min_value=1, required=True)


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
            'machine_gen_code_detection_result',
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
