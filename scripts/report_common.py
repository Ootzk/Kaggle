"""Source identity shared by local export and the dependency-free Pages build."""
import hashlib
import json


def source_digest(notebook):
    cells = [
        {
            "cell_type": c["cell_type"],
            "source": "".join(c["source"]),
            **(
                {"hide_input": True}
                if "hide_input" in c.get("metadata", {}).get("tags", [])
                else {}
            ),
        }
        for c in notebook["cells"]
    ]
    return hashlib.sha256(json.dumps(cells, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
