Para obtener los datos:

a) Clinical trials:
- endpoint: studies ("https://clinicaltrials.gov/api/v2/studies")
- parametros: {"query.cond": "epilepsy", "pageSize"= 300}
- fecha: 01/10/2026

b) OpenFDA:
- endpoint: drug -> event ("https://api.fda.gov/drug/event.json")
- parametros: {"search": i, "limit"=100} -> i va cambiando dentro de un ciclo: for i in ["cannabidiol", "levetiracetam", "carbamazepine"]
- fecha: 01/10/2026

c) PubMed:
- endpoint: eutils ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
- parametros: {
        "db": "pubmed",
        "term": i,
        "retmode": "json",
        "retmax": max_results
    } -> i va cambiando dentro de un ciclo: for i in ["cannabidiol", "levetiracetam", "carbamazepine"]
- fecha: 01/10/2026