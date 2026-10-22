import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def build_index(df):
    """
    Combine key fields into one rich text string per row
    so the AI searches across failure, cause AND part info.
    """
    combined_texts = (
        "Failure: " + df['Failure Description'].astype(str) + " | " +
        "Cause: " + df.get('Cause Assessment', pd.Series(['Unknown']*len(df))).astype(str) + " | " +
        "Part: " + df.get('Defective Part Number Description', pd.Series(['Unknown']*len(df))).astype(str)
    )
    embeddings = model.encode(combined_texts.tolist(), show_progress_bar=True)
    return embeddings

def find_similar_failures(query, df, embeddings, top_k=5):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    
    top_indices = np.argsort(similarities)[::-1][:top_k]
    top_scores = similarities[top_indices]
    
    results = df.iloc[top_indices].copy()
    results['Similarity %'] = (top_scores * 100).round(1)
    
    return results