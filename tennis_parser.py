from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher

KNOWN_OPPONENTS = [
    {"id": 1, "name": "Marco Rossi"},
    {"id": 2, "name": "Luca Bianchi"},
    {"id": 3, "name": "Andrea Verdi"},
]

SET_PATTERN = re.compile(r"(\d)\s*[-:]\s*(\d)(?:\((\d)\s*[-:]\s*(\d)\))?")
OPPONENT_PATTERN = re.compile(
    r"(?:contro|vs\.?|avversario)\s+([A-Za-zÀ-ÿ' ]{3,40}?)(?=\s+e\s+ho|\s+ho\s+|,|\.|\d|$)",
    re.IGNORECASE,
)


@dataclass
class Tiebreak:
    user: int
    opponent: int


@dataclass
class SetScore:
    user_games: int
    opponent_games: int
    tiebreak: Tiebreak | None = None


@dataclass
class Opponent:
    raw_name: str | None = None
    normalized_name: str | None = None
    matched_opponent_id: int | None = None
    confidence: float = 0.0


def _is_valid_set(user_games: int, opponent_games: int, tiebreak: Tiebreak | None) -> bool:
    pairs = {(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (7, 5), (7, 6)}
    if (user_games, opponent_games) in pairs or (opponent_games, user_games) in pairs:
        if 7 in (user_games, opponent_games) and 6 in (user_games, opponent_games):
            return tiebreak is not None
        return True
    return False


def _extract_sets(text: str) -> tuple[list[SetScore], list[str]]:
    sets: list[SetScore] = []
    key_events: list[str] = []

    for match in SET_PATTERN.finditer(text):
        user_games = int(match.group(1))
        opponent_games = int(match.group(2))
        tb_u = match.group(3)
        tb_o = match.group(4)

        tiebreak = Tiebreak(user=int(tb_u), opponent=int(tb_o)) if tb_u and tb_o else None
        if _is_valid_set(user_games, opponent_games, tiebreak):
            sets.append(SetScore(user_games=user_games, opponent_games=opponent_games, tiebreak=tiebreak))

    low = text.lower()
    if "doppio fallo" in low or "doppi falli" in low:
        key_events.append("Molti doppi falli segnalati")
    if "seconda" in low:
        key_events.append("Rendimento sulla seconda da migliorare")
    if "break" in low:
        key_events.append("Menzionati break decisivi")

    return sets, key_events


def _extract_opponent(text: str) -> Opponent:
    match = OPPONENT_PATTERN.search(text)
    if not match:
        return Opponent()

    raw_name = " ".join(match.group(1).strip().split())
    normalized = raw_name.lower()

    best_id = None
    best_score = 0.0
    for candidate in KNOWN_OPPONENTS:
        ratio = SequenceMatcher(None, normalized, candidate["name"].lower()).ratio()
        if ratio > best_score:
            best_score = ratio
            best_id = candidate["id"]

    if best_score < 0.65:
        best_id = None

    return Opponent(raw_name=raw_name, normalized_name=normalized, matched_opponent_id=best_id, confidence=round(best_score, 2))


def _compute_winner(sets: list[SetScore]) -> str:
    user_sets = sum(1 for s in sets if s.user_games > s.opponent_games)
    opp_sets = sum(1 for s in sets if s.user_games < s.opponent_games)
    if user_sets > opp_sets:
        return "user"
    if opp_sets > user_sets:
        return "opponent"
    return "unknown"


def _confidence(sets: list[SetScore], opponent: Opponent, text: str) -> float:
    score = 0.35
    if sets:
        score += min(0.35, 0.12 * len(sets))
    if opponent.raw_name:
        score += 0.15
    if len(text.split()) > 12:
        score += 0.1
    score += min(0.1, opponent.confidence * 0.1)
    return round(min(score, 0.98), 2)


def _generate_insights(text: str) -> list[dict[str, str]]:
    low = text.lower()
    insights: list[dict[str, str]] = []

    if "doppio fallo" in low or "doppi falli" in low:
        insights.append(
            {
                "category": "tecnico",
                "observation": "Hai riportato diversi doppi falli.",
                "suggested_action": "Allenare 2a di servizio con target profondi: 4 serie da 20 palle.",
                "priority": "alta",
            }
        )

    if "tie-break" in low or "tiebreak" in low:
        insights.append(
            {
                "category": "mentale",
                "observation": "Sono emersi momenti ad alta pressione nel tie-break.",
                "suggested_action": "Routine pre-punto (respirazione + parola chiave) nei punti > 30-30.",
                "priority": "media",
            }
        )

    if not insights:
        insights.append(
            {
                "category": "tattico",
                "observation": "Report con pochi dettagli tattici specifici.",
                "suggested_action": "Nel prossimo report indica direzioni servizio, pattern 1-2 colpi e punti chiave.",
                "priority": "media",
            }
        )

    return insights[:5]


def parse_report(report_text: str) -> dict:
    sets, key_events = _extract_sets(report_text)
    opponent = _extract_opponent(report_text)
    winner = _compute_winner(sets)
    extraction_confidence = _confidence(sets, opponent, report_text)

    return {
        "winner": winner,
        "score": {"sets": [asdict(s) for s in sets]},
        "opponent": asdict(opponent),
        "key_events": key_events,
        "extraction_confidence": extraction_confidence,
        "insights": _generate_insights(report_text),
    }


def parse_report_json(report_text: str) -> str:
    return json.dumps(parse_report(report_text), ensure_ascii=False, indent=2)
