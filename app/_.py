import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss

# 1. Initialize Open-Source Embedding and Reranker Models locally on your machine
# all-MiniLM-L6-v2 maps text to a 384-dimensional vector space.
# ms-marco-MiniLM-L-6-v2 evaluates the deep cross-attention text similarity score.
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# 2. Production Corpus: Authentic Underwriting & Auditing Credit Guidelines
COMPLIANCE_CORPUS = [
    "Credit Bureau Governance Mandate: Any application displaying a primary bureau CIBIL score under 650 must be tagged as an automated risk rejection at the gate level, unless explicit collateral security coverage exceeding 150% of the principal requested amount is pledged as an offset liability.",
    "Unsecured MSME Cash Flow Exposure Limits: Loans lacking explicit physical asset backs are capped at a strict Debt-to-Income (DTI) ratio ceiling of 45%. Any calculated DTI beyond 45% represents a material breach of Reserve Bank of India retail exposure guidelines and cannot be approved without a credit-committee override flag.",
    "Secured Collateral Margin Requirements: For all secured credit facilities, the Loan-to-Value (LTV) ratio must maintain a safety buffer margin under 80%. If capital request structures push the calculated LTV between 80.01% and 90%, a mandatory Regional Risk Manager sign-off block must be written into the execution ledger.",
    "Entity Stability and Tenure Mandate: To qualify for unsecured commercial working capital, active entities operating under a sole proprietorship, partnership, or private limited framework must demonstrate a minimum continuous operational business vintage of 3 full uninterrupted fiscal years, verified via active GST registration dates.",
    "Retail Salaried Risk Underwriting Guidelines: Individual applicants classified as salaried workers must verify a continuous employment tenure baseline of 1.5 years with their current employer, backed by consecutive corporate Provident Fund (PF) contribution logs.",
    "Statutory Financial Audit Verification: All commercial loan facilities exceeding a principal request threshold of INR 5,00,000 require a verified Income Tax Return (ITR) filed status for the preceding 2 fiscal cycles. Missing or unverified ITR records constitute an automatic compliance deficit, short-circuiting the transaction routing path to a terminal REJECTED state."
]

# 3. Compile local Vector Database using FAISS
# Transform the textual policy strings into mathematical vector matrices
text_embeddings = embedding_model.encode(COMPLIANCE_CORPUS, convert_to_numpy=True)
dimension = text_embeddings.shape[1]

# Instantiate an optimized L2-distance FAISS index matrix and load the rows
vector_index = faiss.IndexFlatL2(dimension)
vector_index.add(text_embeddings)


def execute_advanced_rag_lookup(query: str, top_k_vector: int = 4, top_n_rerank: int = 2) -> list[str]:
    """
    Executes a complete 2-Stage Advanced RAG sequence:
    Stage 1: Dense Semantic Vector Retrieval via the local FAISS index (optimized for speed/recall).
    Stage 2: Deep Contextual Reranking via a Cross-Encoder network (optimized for precision).
    """
    # --- STAGE 1: VECTOR RETRIEVAL (Broad Search) ---
    query_vector = embedding_model.encode([query], convert_to_numpy=True)
    
    # Query FAISS index for the top K closest matches based on Euclidean distance
    _, indices = vector_index.search(query_vector, top_k_vector)
    
    # Extract raw text chunks matching the top indexed vector hits
    retrieved_chunks = [COMPLIANCE_CORPUS[idx] for idx in indices[0] if idx != -1]
    
    if not retrieved_chunks:
        return ["Default Governance Policy: General corporate financial risk parameters apply."]
        
    # --- STAGE 2: CROSS-ENCODER RERANKING (Deep Text Scoring) ---
    # Construct pairs of (query, document_chunk) for the cross-attention network
    rerank_pairs = [[query, chunk] for chunk in retrieved_chunks]
    
    # Compute the true semantic relevance scores between the query and the documents
    similarity_scores = reranker_model.predict(rerank_pairs)
    
    # Sort the document indices based on scores in descending order
    sorted_indices = np.argsort(similarity_scores)[::-1]
    
    # Filter strictly down to the top N context clauses to completely eliminate LLM context noise
    final_reranked_chunks = [retrieved_chunks[idx] for idx in sorted_indices[:top_n_rerank]]
    
    return final_reranked_chunks