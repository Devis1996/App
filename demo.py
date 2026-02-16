from tennis_parser import parse_report_json

if __name__ == "__main__":
    sample = (
        "Ho giocato contro Marco Rossi e ho vinto 6-4 3-6 7-6(7-5). "
        "Nel secondo set ho fatto troppi doppi falli, ma nel tie-break sono rimasto lucido."
    )
    print(parse_report_json(sample))
