from dataclasses import dataclass
@dataclass(frozen=True)
class Instrument:
    instrument_id:str
    version:str
    dimensions:tuple[str,...]
