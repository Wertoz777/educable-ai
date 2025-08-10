from dataclasses import dataclass
import copy, time

@dataclass
class ValueModel:
    version: int
    axioms: dict
    notes: str = ""

class CVE:
    def __init__(self, seed: ValueModel):
        self.active = seed
        self.history = [copy.deepcopy(seed)]  # identity-preserving

    def propose_update(self, delta: dict, reason: str):
        vm = copy.deepcopy(self.active)
        vm.version += 1
        vm.notes = f"reason={reason} ts={time.time()}"
        for ax, changes in delta.items():
            vm.axioms[ax].update(changes)
        return vm

    def commit(self, vm, receipt_id: str):
        self.history.append(copy.deepcopy(vm))
        self.active = vm
        self._audit("commit", vm.version, receipt_id)

    def rollback(self, version: int):
        for m in self.history:
            if m.version == version:
                self.active = copy.deepcopy(m)
                self._audit("rollback", version, "manual")
                return
        raise ValueError("version_not_found")

    def _audit(self, action, version, ref):
        print({"action": action, "version": version, "ref": ref})