from vectorSearch import VectorSearch



vs = VectorSearch()


result = vs.search("Explain the project", threshold=0.5)
print(result)