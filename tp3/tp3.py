from collections import Counter
import re
import math
def charger_documents(chemin):
    documents = {}
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne:
                continue
            doc_id, texte = ligne.split("\t", 1)
            documents[doc_id] = texte
    return documents

documents = charger_documents("documents.tsv")
#EX2
STOPWORDS = {
    "a", "an", "the", "and", "or", "not", "of", "in", "to", "for", "is", "are", "it",
    "its", "by", "with", "as", "at", "on", "over", "into", "than", "then", "that",
    "this", "each", "how", "many", "unlike", "according", "between", "which", "from",
}
def stem(token):
    if (len(token)<=3):
        return token
    if token.endswith("ies") and len(token) > 4:
        token = token[:-3] + "y"
    elif token.endswith(("sses", "xes", "ches", "shes")):
        token = token[:-2]
    elif token.endswith("s") and not token.endswith(("ss", "us", "is")):
        token = token[:-1]
    if token.endswith("ing") and len(token) > 5:
        token = token[:-3]
    elif token.endswith("ed") and len(token) > 4:
        token = token[:-2]
    return token
def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())#passage en miniscule + tokenization
def preprocess(text):
    tokens=tokenize(text)
    tokens=[t for t in tokens if t not in STOPWORDS] #suppression les stopwords de tokens
    tokens=[stem(t) for t in tokens]
    return tokens
def afficher_pipeline(doc_id):
    texte = documents[doc_id]
    tokens = tokenize(texte)
    sans_stop = [t for t in tokens if t not in STOPWORDS]
    indexes = preprocess(texte)

    print(f"[{doc_id}] texte original : {texte}")
    print(f"     tokens              : {tokens}")
    print(f"     sans mots vides     : {sans_stop}")
    print(f"     termes indexés      : {indexes}\n")

"""for d in ("D1", "D4", "D7"):
    afficher_pipeline(d)"""
#EX3
def construire_index_enrichi(documents):
    index = {}
    for doc_id, texte in documents.items():
        for terme, tf in Counter(preprocess(texte)).items():
            entree = index.setdefault(terme, {"df": 0, "postings": {}})
            entree["postings"][doc_id] = {"tf": tf}
            entree["df"] += 1
    return index
def afficher_index(index, limite=None):
    print(f"{'TERM':<14}{'DF':<4}POSTINGS")
    for i, (t, e) in enumerate(sorted(index.items())):
        if limite and i >= limite:
            print("..."); break
        post = ", ".join(f"{d}(tf={p['tf']})" for d, p in e["postings"].items())
        print(f"{t:<14}{e['df']:<4}{post}")


#EX4
def calculer_idf(terme, index_inverse, N):
    if terme not in index_inverse:
        return 0.0
    return math.log10(N / index_inverse[terme]["df"])
#ex5
def poids_tfidf(terme, doc_id, index_inverse, N):
    entree = index_inverse.get(terme)
    if entree is None or doc_id not in entree["postings"]:
        return 0.0
    tf = entree["postings"][doc_id]["tf"]
    return (1 + math.log10(tf)) * calculer_idf(terme, index_inverse, N)
#EX6
index_inverse = construire_index_enrichi(documents)
vocabulary = sorted(index_inverse.keys())
N = len(documents)

def document_vector(doc_id, vocabulary, index_inverse, N):
    return [poids_tfidf(t, doc_id, index_inverse, N) for t in vocabulary]

"""for d in ("D1", "D2", "D3"):
    v = document_vector(d, vocabulary, index_inverse, N)
    nuls = sum(1 for x in v if x == 0)
    print(f"{d} : {len(v)} composantes, {nuls} nulles ({100*nuls/len(v):.1f} %)")
    print("   vecteur complet :", [round(x, 3) for x in v])
    print("   non nulles      :", {vocabulary[i]: round(x, 3) for i, x in enumerate(v) if x != 0}, "\n")"""
#EX7
def query_vector(query, vocabulary, index_inverse, N):
    tf_q = Counter(preprocess(query))
    vec = []
    for t in vocabulary:
        tf = tf_q.get(t, 0)
        vec.append((1 + math.log10(tf)) * calculer_idf(t, index_inverse, N) if tf > 0 else 0.0)
    return vec
"""q = "information retrieval model"
vq = query_vector(q, vocabulary, index_inverse, N)

print(f"Requête : {q}")
print(f"{'TERM':<14}{'TF':<4}{'IDF':<9}POIDS")
tf_q = Counter(preprocess(q))
for i, w in enumerate(vq):
    if w != 0:
        t = vocabulary[i]
        print(f"{t:<14}{tf_q[t]:<4}{calculer_idf(t, index_inverse, N):<9.4f}{w:.4f}")
        """
#EX8
def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    if n1 == 0 or n2 == 0:      # cas d'une norme nulle -> score 0 (évite la division par zéro)
        return 0.0
    return dot / (n1 * n2)
"""q = "information retrieval model"
vq = query_vector(q, vocabulary, index_inverse, N)

print(f"Requête : {q}\n")
print(f"{'DocID':<7}Score")
for doc_id in documents:
    vd = document_vector(doc_id, vocabulary, index_inverse, N)
    print(f"{doc_id:<7}{cosine_similarity(vq, vd):.4f}")"""

# test explicite du cas norme nulle
print("\nTest vecteur nul :", cosine_similarity([0, 0, 0], [1, 2, 3]))
#EX9
def search(query, documents, index_inverse, vocabulary, N, k=5):
    # 1-2. prétraitement de la requête + vecteur requête (même espace que les documents)
    vq = query_vector(query, vocabulary, index_inverse, N)

    # 3. similarité cosinus entre la requête et chaque document
    results = []
    for doc_id in documents:
        vd = document_vector(doc_id, vocabulary, index_inverse, N)
        score = cosine_similarity(vq, vd)
        # 4. on élimine les scores nuls
        if score > 0:
            results.append((doc_id, score))

    # 5. tri par score décroissant (à égalité : par DocID)
    results.sort(key=lambda x: (-x[1], x[0]))

    # 6. les k premiers résultats
    return results[:k]


def afficher_resultats(query, results, documents):
    print(f"\nQuery > {query}")
    print(f"TOP-{len(results)} RESULTS")
    print(f"{'Rank':<6}{'DocID':<7}{'Score':<9}Document")
    print("-" * 80)
    for rank, (doc_id, score) in enumerate(results, 1):
        print(f"{rank:<6}{doc_id:<7}{score:<9.4f}{documents[doc_id]}")


"""requetes = [
    "information retrieval model",
    "dense retrieval embeddings",
    "inverted index search engines",
    "boolean model operators",
    "bm25 ranking function",
]
for q in requetes:
    afficher_resultats(q, search(q, documents, index_inverse, vocabulary, N, k=5), documents)
"""
#ex11
def recherche_booleenne_and(query, index_inverse, use_stemming=False):
    termes = preprocess(query, use_stemming)
    if not termes or any(t not in index_inverse for t in termes):
        return []
    ensembles = [set(index_inverse[t]["postings"]) for t in termes]
    return sorted(set.intersection(*ensembles), key=lambda d: int(d[1:]))
