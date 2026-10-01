import json
import logging
import os
import re
import time
from datetime import datetime

import pandas as pd
import requests
import requests_cache
from pydantic import BaseModel, ValidationError, field_validator, model_validator
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


class ClinicalTrialsExtractor:
    def __init__(self, cache_name="ct_api_cache", expire_after=86400):
        self.real_requests = 0
        self.cache_handled = 0
        self.session = requests_cache.CachedSession(
            cache_name=cache_name, backend="sqlite", expire_after=expire_after
        )
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        def count_requests(response, *args, **kwargs):
            if getattr(response, "from_cache", False):
                self.cache_handled += 1
            else:
                self.real_requests += 1

        self.session.hooks["response"].append(count_requests)

    def get_trials(self, condition: str, max_records: int = 100) -> list:
        url = "https://clinicaltrials.gov/api/v2/studies"
        params = {"query.cond": condition, "pageSize": 100}

        raw_generator = self.paginar(url, params)
        raw_studies = list(raw_generator)[:max_records]

        return raw_studies

    def paginar(self, url, params):
        token = None
        while True:
            r = self.session.get(url, params={**params, "pageToken": token}, timeout=30)
            r.raise_for_status()
            datos = r.json()
            yield from datos.get("studies", [])
            token = datos.get("nextPageToken")
            if not token:
                break

    @staticmethod
    def process_study(study):
        protocol = study.get("protocolSection", {})
        id_module = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        design_module = protocol.get("designModule", {})

        return {
            "nctId": id_module.get("nctId"),
            "briefTitle": id_module.get("briefTitle"),
            "lastUpdateSubmitDate": status_module.get("lastUpdateSubmitDate"),
            "studyType": design_module.get("studyType"),
        }

    def process_studies_by_generator(self, url, params, n):
        records = []
        for i, study in enumerate(self.paginar(url, params)):
            if i >= n:
                break
            record = self.process_study(study)
            records.append(record)
        return records

    def process_studies_in_memory(self, url, params, n):
        all_studies = list(self.paginar(url, params))[:n]
        return [self.process_study(study) for study in all_studies]

    def save_raw(self, url, params, n, filename="raw_studies", filepath=None):
        raw_studies = list(self.paginar(url, params))[:n]
        payload = {
            "metadata": {
                "download_date": datetime.tz.now().isoformat(),
                "source_url": url,
                "parameters": params,
                "records_extracted": len(raw_studies),
            },
            "raw_studies": raw_studies,
        }
        if filepath is None:
            filepath = f"../data/raw/{filename}.json"
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        print(f"saved at: {filepath}")

    def print_real_request_stats(self):
        total = self.real_requests + self.cache_handled
        print(f"Total requests: {total}")
        print(f"\t-> Real requests: {self.real_requests}")
        print(f"\t-> Handled by cache: {self.cache_handled}")


def paginar(url, params):
    token = None
    while True:
        r = requests.get(url, params={**params, "pageToken": token}, timeout=30)
        r.raise_for_status()
        datos = r.json()
        yield from datos["studies"]
        token = datos.get("nextPageToken")
        if not token:
            break


def process_study(study):
    """
    procesamiento estudio por estudio: extraer su Id, titulo, ultima fecha de actualizacion y tipo de estudio
    """
    protocol = study.get("protocolSection", {})
    id_module = protocol.get("identificationModule", {})
    status_module = protocol.get("statusModule", {})
    design_module = protocol.get("designModule", {})

    return {
        "nctId": id_module.get("nctId"),
        "briefTitle": id_module.get("briefTitle"),
        "lastUpdateSubmitDate": status_module.get("lastUpdateSubmitDate"),
        "studyType": design_module.get("studyType"),
    }


def process_studies_by_generator(url, params, n):
    records = []
    for i, study in enumerate(paginar(url, params)):
        if i >= n:
            break
        record = process_study(study)
        records.append(record)
    return records


def process_studies_in_memory(url, params, n):
    all_studies = list(paginar(url, params))[
        :n
    ]  # convertir a lista para obligar a generador a cargar en memoria
    records = [process_study(study) for study in all_studies]
    return records


def extract_openfda_events(drug_name, limit=100):
    api_key = os.getenv("OPENFDA_API_KEY")
    url = "https://api.fda.gov/drug/event.json"
    params = {}
    if api_key:
        params["api_key"] = api_key
        delay = 0.25
    else:
        delay = 0.5
    params["search"] = (f'patient.drug.medicinalproduct:"{drug_name}"',)
    params["limit"] = min(limit, 100)
    time.sleep(delay)
    response = requests.get(url, params=params, timeout=30)
    if response.status_code == 404:
        print("no open fda records found")
        return []
    response.raise_for_status()
    results = response.json().get("results", [])
    print(f"retrieved {len(results)} openfda records for {drug_name} drug")
    return results


def extract_pubmed_articles(search_term, max_results=10):
    api_key = os.getenv("PUBMED_API_KEY")
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    search_params = {}
    if api_key:
        search_params["api_key"] = api_key
        delay = 0.11
    else:
        delay = 0.35
    search_params.update(
        {"db": "pubmed", "term": search_term, "retmode": "json", "retmax": max_results}
    )
    time.sleep(delay)
    search_response = requests.get(
        f"{base_url}/esearch.fcgi", params=search_params, timeout=30
    )
    search_response.raise_for_status()
    id_list = search_response.json().get("esearchresult", {}).get("idlist", [])
    if not id_list:
        print("no pubmed articles found")
        return []
    summary_params = {}
    if api_key:
        summary_params["api_key"] = api_key
    summary_params.update({"db": "pubmed", "id": ",".join(id_list), "retmode": "json"})
    time.sleep(delay)
    if api_key:
        summary_params["api_key"] = api_key
    summary_response = requests.get(
        f"{base_url}/esummary.fcgi", params=summary_params, timeout=30
    )
    summary_response.raise_for_status()
    results = summary_response.json().get("result", {})
    articles = [article_data for key, article_data in results.items() if key != "uids"]
    print(f"retrieved {len(articles)} articles for {search_term} query")
    return articles


class ClinicalTrial(BaseModel):
    nct_id: str
    title: str
    overall_status: str
    enrollment: int | None = None

    @model_validator(mode="before")
    @classmethod
    def flatten_raw(cls, data: dict):
        protocol = data.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        return {
            "nct_id": ident.get("nctId"),
            "title": ident.get("briefTitle"),
            "overall_status": status.get("overallStatus"),
            "enrollment": design.get("enrollmentInfo", {}).get("count"),
        }

    @field_validator("enrollment", mode="before")
    @classmethod
    def parse_enrollment(cls, v):
        if isinstance(v, dict) and "count" in v:
            return v.get("count")
        return v

    @field_validator("enrollment")
    @classmethod
    def check_positive_enrollment(cls, v):
        if v is not None and v < 0:
            raise ValueError("Enrollment cannot be negative")
        return v

    @model_validator(mode="after")
    def check_completed_trials(self):
        if self.overall_status == "COMPLETED" and (
            self.enrollment is None or self.enrollment == 0
        ):
            raise ValueError(
                f"Trial {self.nct_id} is supposed to be completed but has 0 enrollment."
            )
        return self


def validate_clinical_trials(raw_studies: list) -> list:
    valid_records = []

    for study in raw_studies:
        try:
            validated_trial = ClinicalTrial(**study)
            valid_records.append(validated_trial.model_dump())
        except ValidationError as e:
            nct_id = (
                study.get("protocolSection", {})
                .get("identificationModule", {})
                .get("nctId", "Unknown_ID")
            )
            error_messages = [
                f"{err['loc'][0] if err.get('loc') else 'Model'}: {err['msg']}"
                for err in e.errors()
            ]

            logger.warning(
                f"Dropped trial {nct_id}.\t -ValidationError: {error_messages}"
            )
    print(
        f"Processed {len(raw_studies)} records. Kept: {len(valid_records)}. Dropped: {len(raw_studies) - len(valid_records)}."
    )
    return valid_records


class AdverseEvent(BaseModel):
    report_id: str
    serious: int
    patient_sex: int | None = None
    patient_age: float | None = None
    patient_weight: float | None = None
    reactions: list[str]

    @model_validator(mode="before")
    @classmethod
    def extract_patient_data(cls, data: dict):
        patient = data.get("patient", {})

        sex = patient.get("patientsex")
        age = patient.get("patientonsetage")
        weight = patient.get("patientweight")
        raw_reactions = patient.get("reaction", [])
        reaction_list = [
            r.get("reactionmeddrapt")
            for r in raw_reactions
            if isinstance(r, dict) and r.get("reactionmeddrapt")
        ]

        return {
            "report_id": data.get("safetyreportid", "Unknown_ID"),
            "serious": int(data.get("serious", 0)),
            "patient_sex": int(sex) if sex and str(sex).isdigit() else None,
            "patient_age": float(age) if age else None,
            "patient_weight": float(weight) if weight else None,
            "reactions": reaction_list,
        }

    @field_validator("patient_sex")
    @classmethod
    def validate_biological_sex(cls, v):
        if v not in [None, 1, 2]:
            raise ValueError(f"Sex must be 1 (male) or 2 (female), but '{v}' was found")
        return v

    @field_validator("patient_age")
    @classmethod
    def check_biological_age(cls, v):
        if v is not None and (v < 0 or v > 120):
            raise ValueError(f"Age must be within 0 and 120 years, but {v} was found")
        return v

    @field_validator("patient_weight")
    @classmethod
    def check_plausible_weight(cls, v):
        if v is not None and (v <= 0 or v > 500):
            raise ValueError(
                f"Weight in kg must be within 0.1-500 range, but {v} was found"
            )
        return v


def validate_adverse_events(raw_events: list) -> list:
    valid_records = []
    for event in raw_events:
        try:
            validated_event = AdverseEvent(**event)
            valid_records.append(validated_event.model_dump())

        except ValidationError as e:
            report_id = event.get("safetyreportid", "Unknown_ID")
            error_messages = [
                f"{err['loc'][0] if err.get('loc') else 'Model'}: {err['msg']}"
                for err in e.errors()
            ]
            logger.warning(
                f"Dropped FDA adverse event {report_id}.\t -ValidationError: {error_messages}"
            )

    print(
        f"Processed {len(raw_events)} records. Kept: {len(valid_records)}. Dropped: {len(raw_events) - len(valid_records)}."
    )
    return valid_records


class PubMedArticle(BaseModel):
    uid: str
    title: str
    pub_date: str
    source: str
    authors: list[str]

    @model_validator(mode="before")
    @classmethod
    def extract_article_data(cls, data: dict):
        raw_authors = data.get("authors", [])
        author_names = [
            a.get("name") for a in raw_authors if isinstance(a, dict) and a.get("name")
        ]
        return {
            "uid": data.get("uid", "Unknown_UID"),
            "title": data.get("title", "No Title"),
            "pub_date": data.get("pubdate", ""),
            "source": data.get("source", "Unknown Source"),
            "authors": author_names,
        }

    @field_validator("authors")
    @classmethod
    def check_authors_n(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Article without registered authors")
        return v

    @field_validator("pub_date")
    @classmethod
    def validate_publication_year(cls, v):
        if not v:
            raise ValueError("Publication date is missing")
        match = re.search(r"\d{4}", v)
        if not match:
            raise ValueError(f"Could not extract a valid 4-digit year from date '{v}'")

        year = int(match.group(0))
        current_year = datetime.tz.now().year

        if year < 1800 or year > current_year + 1:
            raise ValueError(f"Publication year {year} is impossible.")

        return v


def validate_pubmed_articles(raw_articles: list) -> list:
    valid_records = []

    for article in raw_articles:
        try:
            validated_article = PubMedArticle(**article)
            valid_records.append(validated_article.model_dump())

        except ValidationError as e:
            uid = article.get("uid", "Unknown_UID")
            error_messages = [
                f"{err['loc'][0] if err.get('loc') else 'Model'}: {err['msg']}"
                for err in e.errors()
            ]
            logger.warning(
                f"Dropped Article {uid}.\t -ValidationError: {error_messages}"
            )

    print(
        f"Processed {len(raw_articles)} records. Kept: {len(valid_records)}. Dropped: {len(raw_articles) - len(valid_records)}."
    )
    return valid_records


def normalize_fda_pubmed(validated_dict):
    dfs = []
    for drug_name, records in validated_dict.items():
        if not records:
            continue
        df = pd.json_normalize(records)
        df.insert(0, "query_drug", drug_name)
        dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()


def normalize_clinical_trials(
    validated_records: list, query_label: str
) -> pd.DataFrame:
    if not validated_records:
        return pd.DataFrame()
    df = pd.json_normalize(validated_records)
    if query_label is not None:
        df.insert(0, "query_label", query_label)

    return df
