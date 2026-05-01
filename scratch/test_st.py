import sentence_transformers
print("Sentence Transformers version:", sentence_transformers.__version__)
model = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully")
emb = model.encode(["hello world"])
print("Embedding shape:", emb.shape)
