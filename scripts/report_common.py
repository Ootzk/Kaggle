"""Source identity shared by local export and the dependency-free Pages build."""
import hashlib
import json


def source_digest(notebook):
    cells = [
        {"cell_type": c["cell_type"], "source": "".join(c["source"])}
        for c in notebook["cells"]
    ]
    return hashlib.sha256(json.dumps(cells, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
