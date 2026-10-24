"""
GreenPulse AI Copilot - Intent Classifier
Analyzes natural language user input to determine the required execution path:
- LIVE_DATA (Real-time telemetry, forecasts, alerts, recommendations)
- RAG_DOCS (Vector search over company SOPs, manuals, standards, schemes)
- INDUSTRIAL_KNOWLEDGE (Domain conceptual definitions and formulations)
- HYBRID (Correlates live telemetry with regulatory standards or SOP thresholds)
"""
import re
from enum import Enum
from typing import Dict, List, Optional, Tuple


class QueryIntent(str, Enum):
    LIVE_DATA = "LIVE_DATA"
    RAG_DOCS = "RAG_DOCS"
    INDUSTRIAL_KNOWLEDGE = "INDUSTRIAL_KNOWLEDGE"
    HYBRID = "HYBRID"
    GREETING = "GREETING"


class IntentClassifier:
    """Classifies user query intent using pattern matching, entities, and keywords."""

    GREETING_PHRASES = [
        "what is your name", "what's your name", "who are you", "what are you",
        "introduce yourself", "what can you do", "help me", "how do you work",
        "good morning", "good afternoon", "good evening", "greetings"
    ]
    GREETING_WORDS = {"hi", "hello", "hey", "help"}

    # Keywords signaling live operational data queries
    LIVE_DATA_TRIGGERS = [
        "today", "now", "current", "live", "real-time", "real time",
        "highest consuming", "highest energy", "lowest energy", "consuming most",
        "why is today", "why is energy high", "energy high", "energy spike",
        "active alerts", "current alerts", "explain current alerts", "open alerts", "explain active",
        "recommendations", "highest roi", "top recommendations", "action plan",
        "forecast", "today's forecast", "24-hour forecast", "tomorrow",
        "dashboard", "summarize today", "summarize dashboard", "plant status",
        "machine status", "machine-01", "machine-02", "machine-03", "comp-01",
        "comp-02", "cnc-01", "cnc-02", "furn-01", "hvac-01", "pump-01",
        "why is machine", "is machine critical", "telemetry", "kwh today"
    ]

    # Keywords signaling RAG document retrieval
    RAG_DOCS_TRIGGERS = [
        "sop", "standard operating procedure", "procedure", "protocol",
        "manual", "oem manual", "user manual", "guide", "handbook",
        "bee", "pat scheme", "escert", "escerts", "government scheme",
        "iso 50001", "iso50001", "enpi", "energy baseline",
        "ieee 519", "ieee", "harmonic limit", "distortion limit",
        "iso 10816", "vibration severity", "zone a", "zone b", "zone c", "zone d",
        "policy", "net zero", "roadmap", "procurement norm",
        "uploaded document", "pdf", "file", "page", "section"
    ]

    # Keywords signaling general industrial AI concept questions
    CONCEPT_TRIGGERS = [
        "what is", "define", "explain concept", "how does", "formula for",
        "difference between", "meaning of", "what does", "concept of",
        "peak demand", "contract demand", "contracted demand", "cmd",
        "power factor", "load factor", "carbon intensity",
        "machine health index", "mhi", "shap", "shapley", "explainability",
        "forecast confidence", "isolation forest", "xgboost",
        "digital twin", "predictive maintenance", "pdm", "oee",
        "equipment utilization", "production efficiency", "sec"
    ]

    def classify(self, query: str) -> Tuple[QueryIntent, Optional[str], Optional[str]]:
        """
        Returns:
            Tuple[QueryIntent, detected_machine_id, target_collection_hint]
        """
        q = query.lower().strip()
        q_words = set(re.findall(r"\b\w+\b", q))

        # Check for Greetings / Introduction / Identity
        if any(p in q for p in self.GREETING_PHRASES) or (bool(q_words.intersection(self.GREETING_WORDS)) and len(q_words) <= 3):
            return QueryIntent.GREETING, None, None

        # Extract potential machine mentions
        detected_machine = self._extract_machine(q)

        has_live = any(trigger in q for trigger in self.LIVE_DATA_TRIGGERS)
        has_rag = any(trigger in q for trigger in self.RAG_DOCS_TRIGGERS)
        has_concept = any(trigger in q for trigger in self.CONCEPT_TRIGGERS)

        # Check for Hybrid query (both live and RAG/standards requested)
        if (has_live and has_rag) or (detected_machine and ("sop" in q or "manual" in q or "limit" in q or "standard" in q)):
            return QueryIntent.HYBRID, detected_machine, self._detect_collection(q)

        # Check for Pure Live Data
        if has_live and not has_rag:
            return QueryIntent.LIVE_DATA, detected_machine, None

        # Check for Pure RAG Docs
        if has_rag:
            return QueryIntent.RAG_DOCS, detected_machine, self._detect_collection(q)

        # Check for Industrial Concept
        if has_concept:
            return QueryIntent.INDUSTRIAL_KNOWLEDGE, detected_machine, None

        # Default fallback: check if question has operational context or document context
        if detected_machine:
            return QueryIntent.LIVE_DATA, detected_machine, None

        # Default to Hybrid/RAG retrieval if unsure
        return QueryIntent.RAG_DOCS, None, None

    def _extract_machine(self, text: str) -> Optional[str]:
        """Detects standard machine identifiers in query text."""
        machine_patterns = [
            r"comp-0?1", r"comp-0?2", r"compressor",
            r"cnc-0?1", r"cnc-0?2", r"milling",
            r"furn-0?1", r"furnace", r"induction",
            r"hvac-0?1", r"chiller",
            r"pump-0?1", r"assy-0?1", r"paint-0?1"
        ]
        for pattern in machine_patterns:
            match = re.search(pattern, text)
            if match:
                val = match.group(0).upper()
                if "COMP" in val or "COMPRESSOR" in val:
                    return "COMP-02" if "2" in val else "COMP-01"
                if "CNC" in val or "MILLING" in val:
                    return "CNC-02" if "2" in val else "CNC-01"
                if "FURN" in val or "FURNACE" in val or "INDUCTION" in val:
                    return "FURN-01"
                if "HVAC" in val or "CHILLER" in val:
                    return "HVAC-01"
                if "PUMP" in val:
                    return "PUMP-01"
                if "PAINT" in val:
                    return "PAINT-01"
                if "ASSY" in val:
                    return "ASSY-01"
        return None

    def _detect_collection(self, text: str) -> Optional[str]:
        """Infers the most relevant collection from query keywords."""
        if any(w in text for w in ["sop", "curtailment", "load shedding", "interlock"]):
            return "company_sops"
        if any(w in text for w in ["manual", "oem", "spec", "spare parts", "lubrication"]):
            return "machine_manuals"
        if any(w in text for w in ["bee", "pat", "escert", "subsidy", "open access"]):
            return "government_schemes"
        if any(w in text for w in ["iso", "iso 50001", "enpi", "baseline"]):
            return "iso_50001"
        if any(w in text for w in ["vibration", "bearing", "grease", "overhaul", "pdm"]):
            return "maintenance_docs"
        if any(w in text for w in ["ieee", "harmonics", "thd", "tdd", "standard"]):
            return "industrial_standards"
        if any(w in text for w in ["policy", "decarbonization", "net zero", "renewable"]):
            return "energy_policies"
        if any(w in text for w in ["plant manual", "facility manual", "general manual", "uploaded", "pdf", "file", "all plant", "general information", "overview manual", "plant #4"]):
            return "uploaded_pdfs"
        return None
