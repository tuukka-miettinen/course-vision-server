from transformers import BertTokenizer, BertModel


class CourseBert:
    def __init__(self):
        self.pretrained_weights = 'bert-base-uncased'
        self.tokenizer = BertTokenizer.from_pretrained(pretrained_weights)
        self.model = BertModel.from_pretrained(pretrained_weights)
    
    def encode(self, courses):
        course_encodings = []
        for course in courses:
            tensors = []
            for sentence in course.description.split('.'):
                input_ids = torch.tensor([self.tokenizer.encode(sentence.lower(), add_special_tokens=True)])
                with torch.no_grad():
                    encoded_layers, _ = model(input_ids)
                    tensors.append(encoded_layers)
            course.encoding = tensors.mean(dim=1).numpy()
        return course_encodings

