import boto3
import json
import faiss
import numpy
import numpy as np
from transformers import BertTokenizer, BertModel
import torch

from dotenv import dotenv_values
config = dotenv_values(".env") 

COURSE_DATA_PATH = 'course_data.json'

client = boto3.client('s3',
    aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])
response = client.download_file(
    Bucket='course.vision-data',
    Key='course_data.json',
    Filename=COURSE_DATA_PATH
)

with open(COURSE_DATA_PATH) as json_file:
    data = json.load(json_file)

class Course:
    def __init__(self,school,department,code,name,description):
        self.school = school
        self.department = department
        self.code = code
        self.name = name
        self.description = description
        self.encoding = None
        
    def __str__(self):
        return f'{self.code} | {self.name}\n{self.description}\n'

courses = []
for school in data['data']['schools']:
    for department in school['departments']:
        for course in department['courses']['feed']:
            code = course['id']
            name = course['details']['name']['en']
            description = course['details']['summary']['content']['en']
            if description:
                courses.append(Course(school['id'], department['name']['en'], code, name, description))

pretrained_weights = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(pretrained_weights)
model = BertModel.from_pretrained(pretrained_weights)

for course in courses:
    tensors = []
    for sentence in course.description.split('.'):
        input_ids = torch.tensor([tokenizer.encode(sentence.lower(), add_special_tokens=True)])
        with torch.no_grad():
            encoded_layers, _ = model(input_ids)
            tensors.append(encoded_layers)
    course.encoding = tensors[0].mean(dim=1).numpy()

d = 768
index = faiss.IndexFlatL2(d)
nof = len(courses)
vecs = np.zeros((nof, d), dtype=np.float32)
for i, course in enumerate(courses):
    vecs[i] = course.encoding
index.add(vecs)

D, I = index.search(vecs, 20)
dynamodb = boto3.resource('dynamodb',
    region_name="eu-central-1",
    aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])
table = dynamodb.Table("course_similarities")

for i in I:
    response = table.put_item(Item={
        "course_id": courses[i[0]].code,
        "similarities": [{
            'course_id': courses[j].code,
            'course_name': courses[j].name
            }
            for j in i[1:]
        ]
    })