import faiss
import numpy

class CourseSearch:
    def __init__(self, dimensions):
        self.d = dimensions
        self.index = faiss.IndexFlatL2(self.d)

    def index(self, courses):
        nof = len(courses)
        vecs = np.zeros((nof, d), dtype=np.float32)
        self.index.add(vecs)