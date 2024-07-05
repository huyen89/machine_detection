import base64
import datetime

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from .models import Submission, ProgrammingLanguage
from .serializers import (
    SubmissionSerializer,
    SubmissionCreateSerializer,
    SubmissionDetailSerializer,
    SubmissionListSerializer
)
from .utils.response_template import ResponseTemplate
from .utils.message_queue import publish_submission_to_queue
from django.conf import settings

import uuid
import os


# Create your views here.
class SubmissionView(APIView):

    def get(self, request, *args, **kwargs):
        submission_list_serializer = SubmissionListSerializer(data=request.query_params)
        submission_list_serializer.is_valid()

        page = 1 if 'page' in submission_list_serializer.errors else submission_list_serializer.data.get('page')
        per_page = 10 if 'per_page' in submission_list_serializer.errors else submission_list_serializer.data.get('per_page')
        sort_by = 'created_at' if 'sort_by' in submission_list_serializer.errors else submission_list_serializer.data.get('sort_by')
        sort_order = 'DESC' if 'sort_order' in submission_list_serializer.errors else submission_list_serializer.data.get('sort_order')

        submissions = Submission.objects.all().order_by(('-' if sort_order == 'DESC' else '') + sort_by)
        paginator = Paginator(submissions, per_page=per_page)
        paginated_submissions = paginator.get_page(page)

        data_list = [submission for submission in paginated_submissions.object_list]
        serializer = SubmissionSerializer(data_list, many=True)

        payload = {
            "page": page,
            "per_page": per_page,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "start": paginated_submissions.start_index(),
            "end": paginated_submissions.end_index(),
            "total": paginator.count,
            "num_pages": paginator.num_pages,
            # "previous_page_number": paginated_submissions.previous_page_number(),
            # "next_page_number": paginated_submissions.next_page_number(),
            "data_list": serializer.data
        }
        return Response(ResponseTemplate.getSuccessResponse("", payload), status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        submission_create_serializer = SubmissionCreateSerializer(data=request.data)
        if not submission_create_serializer.is_valid():
            return Response(
                ResponseTemplate.getErrorResponse("error", submission_create_serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        if not ProgrammingLanguage.objects.filter(id=submission_create_serializer.data.get('programming_language_id')).first():
            return Response(
                ResponseTemplate.getErrorResponse("Language not support"),
                status=status.HTTP_400_BAD_REQUEST
            )

        content = submission_create_serializer.data.get('content')
        decoded_content = base64.b64decode(content).decode('utf-8')
        submission_uuid = str(uuid.uuid4())
        source_file_name = submission_uuid + datetime.datetime.now().strftime(format='%Y_%m_%d_%H_%M_%S')
        base_path = settings.SOURCE_CODE_LOCATION
        source_file_path = os.path.join(base_path, source_file_name)
        with open(source_file_path, "w") as source_file:
            source_file.write(decoded_content)

        data = {
            "name": submission_uuid,
            "filepath": source_file_path,
            "user_id": 1,
            "programming_language_id": submission_create_serializer.data.get('programming_language_id'),
            "machine_gen_detection_status": 0,
        }
        submission_serializer = SubmissionSerializer(data=data)
        submission_serializer.is_valid()
        submission_serializer.save()

        submission_id = submission_serializer.data.get("id")
        if not publish_submission_to_queue(submission_id):
            new_submission = Submission.objects.get(id=submission_id)
            data["machine_gen_detection_status"] = 5
            submission_update_serializer = SubmissionSerializer(instance=new_submission, data=data, partial=True)
            submission_update_serializer.is_valid()
            submission_update_serializer.save()

            return Response(
                ResponseTemplate.getSuccessResponse("New Submission created but cannot analyzed"),
                status=status.HTTP_200_OK
            )

        return Response(
            ResponseTemplate.getSuccessResponse("New Submission created successfully"),
            status=status.HTTP_200_OK
        )


class SubmissionDetailView(APIView):
    def get(self, request, submission_id, *args, **kwargs):
        submission = Submission.objects.filter(id=submission_id).prefetch_related('machine_gen_code_detection_result').first()
        if not submission:
            return Response(
                ResponseTemplate.getErrorResponse("Submission not found"),
                status=status.HTTP_404_NOT_FOUND
            )

        submission_detail_serializer = SubmissionDetailSerializer(instance=submission)
        return Response(
            ResponseTemplate.getSuccessResponse("", submission_detail_serializer.data),
            status=status.HTTP_200_OK
        )

    def delete(self, request, submission_id, *args, **kwargs):
        submission = Submission.objects.filter(id=submission_id).first()
        if not submission:
            return Response(
                ResponseTemplate.getErrorResponse("Submission not found"),
                status=status.HTTP_404_NOT_FOUND
            )

        submission.delete()
        return Response(
            ResponseTemplate.getSuccessResponse("Submission deleted successfully"),
            status=status.HTTP_200_OK
        )


class SubmissionUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        source_file = request.data['source_file']
        programming_language_id = request.data['programming_language_id']

        if not source_file:
            return Response(
                ResponseTemplate.getErrorResponse("Source file is missing"),
                status=status.HTTP_400_BAD_REQUEST
            )

        if not programming_language_id:
            return Response(
                ResponseTemplate.getErrorResponse("Programming Language is missing"),
                status=status.HTTP_400_BAD_REQUEST
            )

        if not ProgrammingLanguage.objects.filter(id=programming_language_id).first():
            return Response(
                ResponseTemplate.getErrorResponse("Language not support"),
                status=status.HTTP_400_BAD_REQUEST
            )

        if source_file.size > 1024*1024*1024:
            return Response(
                ResponseTemplate.getErrorResponse("Source file's size is too big"),
                status=status.HTTP_400_BAD_REQUEST
            )

        fs = FileSystemStorage(location=settings.SOURCE_CODE_LOCATION)
        submission_uuid = str(uuid.uuid4())
        source_file_name = submission_uuid + datetime.datetime.now().strftime(format='%Y_%m_%d_%H_%M_%S')
        fs.save(source_file_name, source_file)

        base_path = settings.SOURCE_CODE_LOCATION
        source_file_path = os.path.join(base_path, source_file_name)

        data = {
            "name": submission_uuid,
            "filepath": source_file_path,
            "user_id": 1,
            "programming_language_id": programming_language_id,
            "machine_gen_detection_status": 0,
        }
        submission_serializer = SubmissionSerializer(data=data)
        submission_serializer.is_valid()
        submission_serializer.save()

        submission_id = submission_serializer.data.get("id")
        if not publish_submission_to_queue(submission_id):
            new_submission = Submission.objects.get(id=submission_id)
            data["machine_gen_detection_status"] = 5
            submission_update_serializer = SubmissionSerializer(instance=new_submission, data=data, partial=True)
            submission_update_serializer.is_valid()
            submission_update_serializer.save()

            return Response(
                ResponseTemplate.getSuccessResponse("New Submission created but cannot analyzed"),
                status=status.HTTP_200_OK
            )

        return Response(
            ResponseTemplate.getSuccessResponse("New Submission created successfully"),
            status=status.HTTP_200_OK
        )
