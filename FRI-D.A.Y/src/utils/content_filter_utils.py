from __future__ import annotations
import json
import re
import fnmatch
import threading
from typing import List, Dict, Any, Optional

try:
    from mitmproxy import http
except Exception:
    http = None

DEFAULT_BLOCKLIST = {
    "domains": [
        "*.doubleclick.net",
        "*.google-analytics.com",
        "*.googlesyndication.com",
        "*.adservice.google.com",
        "*.adsafeprotected.com",
        "*.adnxs.com"
    ],
    "keywords": [
        "malware",
        "adware",
        "spyware",
        "phishing"
    ],
    "regex_patterns": []
}
DEFAULT_PERSIST_PATH = "blocklist.json"
MAX_SCAN_BYTES = 200_000

class ContentFilter:
    def __init__(self, persist: bool = False, persist_path: str = DEFAULT_PERSIST_PATH):
        self._lock = threading.RLock()
        self.persist = bool(persist)
        self.persist_path = persist_path
        self._data: Dict[str, Any] = { "domains": [], "keywords": [], "regex_patterns": [] }
        self._compiled_regex: List[re.Pattern] = []
        self._keywords_lower: List[str] = []
        if self.persist:
            self._load_from_disk()
        else:
            self._data = DEFAULT_BLOCKLIST.copy()
        self._compile_from_data()

    def _load_from_disk(self) -> None:
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k in ("domains", "keywords", "regex_patterns"):
                if k not in data:
                    data[k] = []
            self._data = data
        except FileNotFoundError:
            self._data = DEFAULT_BLOCKLIST.copy()
            self._save_to_disk()
        except Exception:
            self._data = DEFAULT_BLOCKLIST.copy()

    def _save_to_disk(self) -> None:
        try:
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _compile_from_data(self) -> None:
        with self._lock:
            self._compiled_regex = [re.compile(p, re.IGNORECASE) for p in self._data.get("regex_patterns", [])]
            self._keywords_lower = [k.lower() for k in self._data.get("keywords", [])]

    def add_domain(self, domain: str, save: Optional[bool] = None) -> bool:
        with self._lock:
            if domain in self._data["domains"]:
                return False
            self._data["domains"].append(domain)
            if save is None: save = self.persist
            if save: self._save_to_disk()
            return True

    def remove_domain(self, domain: str, save: Optional[bool] = None) -> bool:
        with self._lock:
            if domain in self._data["domains"]:
                self._data["domains"].remove(domain)
                if save is None: save = self.persist
                if save: self._save_to_disk()
                return True
            return False

    def add_keyword(self, keyword: str, save: Optional[bool] = None) -> bool:
        with self._lock:
            if keyword.lower() in (k.lower() for k in self._data["keywords"]):
                return False
            self._data["keywords"].append(keyword)
            if save is None: save = self.persist
            if save: self._save_to_disk()
            self._compile_from_data()
            return True

    def remove_keyword(self, keyword: str, save: Optional[bool] = None) -> bool:
        with self._lock:
            lowercase_list = [k.lower() for k in self._data["keywords"]]
            if keyword.lower() in lowercase_list:
                idx = lowercase_list.index(keyword.lower())
                del self._data["keywords"][idx]
                if save is None: save = self.persist
                if save: self._save_to_disk()
                self._compile_from_data()
                return True
            return False

    def list_rules(self) -> Dict[str, List[str]]:
        with self._lock:
            return { k: list(self._data.get(k, [])) for k in ("domains", "keywords", "regex_patterns") }

    def _match_domain(self, host: str) -> Optional[str]:
        host_l = (host or "").lower()
        for pat in self._data.get("domains", []):
            if fnmatch.fnmatch(host_l, pat.lower()):
                return pat
        return None

    def _match_keyword_in_text(self, text: str) -> Optional[str]:
        tx = (text or "").lower()
        for kw in self._keywords_lower:
            if kw and kw in tx:
                return kw
        return None

    def request(self, flow) -> None:
        if http is None: return
        try:
            host = getattr(flow.request, "host", "")
            url_lower = getattr(flow.request, "pretty_url", "").lower()
            if self._match_domain(host) or self._match_keyword_in_text(url_lower):
                flow.response = http.HTTPResponse.make(403, b"Blocked by F.R.I.D.A.Y. content filter")
        except Exception:
            return

    def response(self, flow) -> None:
        if http is None or not flow.response or not flow.response.content: return
        try:
            content_type = flow.response.headers.get("Content-Type", "").lower()
            if any(ct in content_type for ct in ("text", "html", "json")):
                text = flow.response.get_text(strict=False)
                if text and self._match_keyword_in_text(text):
                    flow.response = http.HTTPResponse.make(403, b"Blocked by F.R.I.D.A.Y. content filter")
        except Exception:
            return

filter_addon = ContentFilter(persist=False)

if http is not None:
    addons = [filter_addon]

def add_domain(domain: str, save: Optional[bool] = None) -> bool:
    return filter_addon.add_domain(domain, save=save)

def remove_domain(domain: str, save: Optional[bool] = None) -> bool:
    return filter_addon.remove_domain(domain, save=save)

def add_keyword(keyword: str, save: Optional[bool] = None) -> bool:
    return filter_addon.add_keyword(keyword, save=save)

def remove_keyword(keyword: str, save: Optional[bool] = None) -> bool:
    return filter_addon.remove_keyword(keyword, save=save)

def list_rules() -> Dict[str, List[str]]:
    return filter_addon.list_rules()

def enable_persistence(path: str = DEFAULT_PERSIST_PATH) -> None:
    with filter_addon._lock:
        filter_addon.persist = True
        filter_addon.persist_path = path
        filter_addon._load_from_disk()
        filter_addon._compile_from_data()



