from typing import Dict, List

from src.core.exceptions import JSONSerializationException
from src.core.utils import atomic_write_json


class JSONSerializer:
    """Serialize metadata with backward-compatible aliases."""

    def serialize(self, metadata_list: List[Dict[str, object]], output_path: str) -> None:
        try:
            payload = {"dataResources": []}
            for entry in metadata_list:
                age = entry.get("age")
                findings = entry.get("findings", [])
                payload["dataResources"].append(
                    {
                        "patient_id": entry.get("patient_id"),
                        "gestational_age": entry.get("gestational_age"),
                        "age": age,
                        "demographic_age": age,
                        "BMI": entry.get("BMI"),
                        "findings": findings,
                        "examination_findings": findings,
                    }
                )

            atomic_write_json(output_path, payload)
        except Exception as exc:
            raise JSONSerializationException(str(exc)) from exc
