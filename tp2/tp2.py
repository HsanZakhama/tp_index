import math
##EX1
def charger_documents(chemin):
    documents = {}
    # On parcourt chaque ligne du fichier une seule fois.
    # Si le fichier contient N lignes, la complexité est O(N).
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne:
                continue
            doc_id, texte = ligne.split("\t", 1)
            documents[doc_id] = texte
    return documents

documents = charger_documents("documents.txt")

"""print(f"Nombre de documents : {len(documents)}")
for doc_id, texte in documents.items():
    print(doc_id, "->", texte)"""

##EX2
def id_num(doc_id):
    """le longeur de doc_id est petit , la fct replace() parcourt la chaine doc_id
    alors o(1)"""
    return int(doc_id.replace("doc","").replace(":",""))
"""c'est pour convertir le nom de doc en int doc1: => 1"""

def index_inv(docs):
    """Construit l'index inversé : mot -> liste triée des documents qui le contiennent."""
    ii={}
    for doc_id in sorted(docs.keys(), key=id_num):"""O(N log N) car sorted() trie les docs"""
        num= id_num(doc_id)
        mots= docs[doc_id].lower().split()
        for mot in mots:
            if mot not in ii:
                ii[mot]=[]
            if not ii[mot] or ii[mot][-1] != num:
                ii[mot].append(num)
    return ii
def afficher_index(index_inverse, limite=15):
    print("\nExtrait de l'index inversé :")
    for i, (mot, docs) in enumerate(sorted(index_inverse.items())):
        if i >= limite:
            print(f"  ... ({len(index_inverse) - limite} autres termes)")
            break
        print(f"  {mot!r:15s} -> {docs}")

ii=index_inv(documents)
"""afficher_index(ii)"""

##EX3

def intersection(list1, list2): 
    i, j = 0, 0 
    result = [] 
    while i < len(list1) and j < len(list2): 
        if list1[i] == list2[j]: 
            result.append(list1[i]) 
            i += 1 
            j += 1 
    
        elif list1[i] < list2[j]: 
            i += 1 
        else: 
            j += 1 
    return result
terme1 = input("Entrez le premier terme : ") 
terme2 = input("Entrez le deuxième terme : ")  
docs1 = ii.get(terme1, []) 
docs2 = ii.get(terme2, []) 
print(f"Intersection : {intersection(docs1, docs2)}")
##EX4

def creer_sauts(liste):
    n = len(liste)

    if n == 0:
        return []

    pas = int(math.sqrt(n))

    if pas < 1:
        pas = 1

    sauts = []

    i = 0
    while i + pas < n:
        sauts.append((i, i + pas))
        i += pas

    return sauts
