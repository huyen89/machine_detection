import os
import torch
from transformers import AutoTokenizer, AutoModel
from rest_framework.decorators import api_view, schema
from rest_framework.response import Response
from django.shortcuts import render
from torch import nn
from rest_framework import status
from django.conf import settings

class Classification(nn.Module):
    def __init__(self):
        super(Classification, self).__init__()
        self.fc1 = nn.Linear(768, 1024)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(1024, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        return x.squeeze()

# Define the model and tokenizer
model_name = "salesforce/codet5p-220m"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).encoder

# Set device and load classification model
device = "cpu"

py_classifier = Classification()
java_classifier = Classification()
cpp_classifier = Classification()

python_path = os.path.join(settings.BASE_DIR, 'api/models/python_checkpoint.pth')
java_path = os.path.join(settings.BASE_DIR, 'api/models/java_checkpoint.pth')
cpp_path = os.path.join(settings.BASE_DIR, 'api/models/cpp_checkpoint.pth')

py_classifier.load_state_dict(torch.load(python_path, map_location=torch.device(device)))
java_classifier.load_state_dict(torch.load(java_path, map_location=torch.device(device)))
cpp_classifier.load_state_dict(torch.load(cpp_path, map_location=torch.device(device)))

py_classifier.eval()
java_classifier.eval()
cpp_classifier.eval()

# Create your views here.
@api_view(['GET'])
@schema(None)
def index_page(request):
    return_data = {
        "error": "0",
        "message": "Successful",
    }
    return Response(return_data, status=status.HTTP_200_OK)

@api_view(["POST"])
@schema(None)
def predict_mgc(request):
    try:
        data = request.data
        print(data)
        content = data.get('content', None)
        language = data.get('language', None)

        if content is None or language is None:
            return Response({
                'error': '1',
                'message': 'Invalid Parameters'
            })

        # Tokenize the input content
        tokenized_input = tokenizer(
            content,
            return_tensors="pt",
            padding='max_length',
            max_length=512,
            truncation=True
        ).to(device)

        # Get [CLS] vector from CodeBERT model and perform classification
        with torch.no_grad():
            codebert_output = model(
                input_ids=tokenized_input['input_ids'].squeeze().view(-1, 512),
                attention_mask=tokenized_input['attention_mask'].squeeze().view(-1, 512)
            ).last_hidden_state[:, 0, :].squeeze()

        if language == "python":
            print(f" [x] Check Python Code.")
            result = py_classifier(codebert_output).item()
        elif language == "cpp":
            print(f" [x] Check C++ Code.")
            result = cpp_classifier(codebert_output).item()
        elif language == "java":
            print(f" [x] Check Java Code.")
            result = java_classifier(codebert_output).item()
        else:
            return Response({
                'error': '1',
                'message': 'Not supported languages'
            })

        predictions = {
            'error': '0',
            'message': 'Successful',
            'prediction': result,
            'confidence_score': result * 100
        }
    except Exception as e:
        predictions = {
            'error': '2',
            "message": str(e)
        }

    return Response(predictions)