import csv
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExternalConcept:
    source: str
    external_id: str
    label: str
    concept_type: str
    payload: dict[str, str]


class DelimitedConceptReader:
    def __init__(
        self,
        path: Path,
        source: str,
        id_columns: tuple[str, ...],
        label_columns: tuple[str, ...],
        type_columns: tuple[str, ...] = (),
    ) -> None:
        self.path = path
        self.source = source
        self.id_columns = id_columns
        self.label_columns = label_columns
        self.type_columns = type_columns

    @staticmethod
    def _first(row: dict[str, str], columns: tuple[str, ...]) -> str:
        for column in columns:
            value = row.get(column, "").strip()
            if value:
                return value
        return ""

    def read(self, delimiter: str = ",") -> Iterable[ExternalConcept]:
        with self.path.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle, delimiter=delimiter):
                external_id = self._first(row, self.id_columns)
                label = self._first(row, self.label_columns)
                concept_type = self._first(row, self.type_columns) if self.type_columns else ""
                if external_id and label:
                    yield ExternalConcept(
                        source=self.source,
                        external_id=external_id,
                        label=label,
                        concept_type=concept_type,
                        payload=dict(row),
                    )


def esco_reader(path: Path) -> DelimitedConceptReader:
    return DelimitedConceptReader(
        path,
        "esco",
        ("conceptUri", "conceptURI", "uri"),
        ("preferredLabel", "preferredlabel", "label"),
        ("conceptType", "concept_type"),
    )


def onet_reader(path: Path) -> DelimitedConceptReader:
    return DelimitedConceptReader(
        path,
        "onet",
        ("O*NET-SOC Code", "O*NET-SOC code", "Code", "code"),
        ("Title", "title", "Name", "name"),
    )


def local_reader(path: Path, source: str = "othello-local") -> DelimitedConceptReader:
    return DelimitedConceptReader(
        path,
        source,
        ("id", "ID", "code", "Code"),
        ("label", "Label", "name", "Name", "title", "Title"),
        ("type", "Type", "concept_type"),
    )
