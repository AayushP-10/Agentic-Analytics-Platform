from __future__ import annotations

from backend.app.services.readers.csv_reader import CSVReader


class TSVReader(CSVReader):
    supported_extensions = {".tsv"}
    format_name = "tsv"
    separator = "\t"
