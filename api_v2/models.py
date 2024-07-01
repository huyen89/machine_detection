from django.db import models


# Create your models here.
class ProgrammingLanguage(models.Model):
    class Meta:
        db_table = 'programming_languages'

    name = models.CharField(max_length=255, unique=True, null=False)
    note = models.CharField(max_length=255, unique=True, null=False)
    created_at = models.DateTimeField(auto_now=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class Submission(models.Model):
    class Meta:
        db_table = 'submissions'

    name = models.CharField(max_length=255, unique=True, null=False)
    filepath = models.CharField(max_length=512, null=False)
    user_id = models.BigIntegerField(default=1)
    coding_problem_id = models.BigIntegerField(null=True)
    programming_language_id = models.BigIntegerField(null=False)
    # programming_language = models.ForeignKey(
    #     ProgrammingLanguage,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     error_messages={"invalid_pk_value": "Programming Language not support"}
    # )
    machine_gen_detection_status = models.SmallIntegerField(null=True)
    code_execution_status = models.SmallIntegerField(null=True)
    code_similarity_detection_status = models.SmallIntegerField(null=True)
    vulnerability_detection_status = models.SmallIntegerField(null=True)
    created_at = models.DateTimeField(auto_now=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.name


class MachineGenCodeDetectionResult(models.Model):
    class Meta:
        db_table = "machine_gen_code_results"

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='machine_gen_code_detection_result')
    probability = models.FloatField(default=0, null=False)
    created_at = models.DateTimeField(auto_now=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

