import json
import os
class Sync:
    def __init__(self, ledger_path="data_storage/hash_ledger.json"):
        self.ledger_path = ledger_path
        if os.path.exists(self.ledger_path):
            with open(self.ledger_path, "r") as f:
                self.seen_ids = set(json.load(f))
        else:
            self.seen_ids = set()
    def is_duplicate(self, chunk_id):
        if chunk_id in self.seen_ids:
            return True 
            
        self.seen_ids.add(chunk_id)
        with open(self.ledger_path, "w") as f:
            json.dump(list(self.seen_ids), f)
        return False