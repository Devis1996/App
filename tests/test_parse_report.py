import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tennis_parser import parse_report


def test_parse_report_with_sets_and_opponent():
    data = parse_report(
        'Ho giocato contro Marco Rossi e ho vinto 6-4 3-6 7-6(7-5). '
        'Nel secondo set ho fatto troppi doppi falli ma nel tie-break sono rimasto lucido.'
    )

    assert data['winner'] == 'user'
    assert len(data['score']['sets']) == 3
    assert data['opponent']['matched_opponent_id'] == 1
    assert data['extraction_confidence'] >= 0.6
    assert len(data['insights']) >= 1


def test_parse_report_without_clear_score():
    data = parse_report('Partita difficile, pochi dettagli.')
    assert data['winner'] == 'unknown'
    assert data['score']['sets'] == []
