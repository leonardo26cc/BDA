import hashlib
import logging
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw_batch_202611"
STAGING = ROOT / "staging" / "verified"
TAMPERED = ROOT / "quarantine" / "tampered"
LOG = ROOT / "logs" / "ejecucion_pipeline.log"


def sha256(path):
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main():
    STAGING.mkdir(parents=True, exist_ok=True)
    TAMPERED.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=LOG, filemode="w", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")

    lines = (RAW / "manifest_checksums.sha256").read_text(encoding="utf-8").splitlines()
    rejected = []
    for line in lines:
        if not line.strip():
            continue
        expected, name = line.split(maxsplit=1)
        name = Path(name.strip().lstrip("*")).name
        source = RAW / name
        target = TAMPERED / name
        if not source.exists() and target.exists():
            source = target
        if not source.exists():
            logging.error("FALTA %s", name)
            continue
        if sha256(source) == expected.lower():
            shutil.copy2(source, STAGING / name)
            logging.info("VERIFICADO %s", name)
            print(f"Verificado: {name}")
        else:
            if source != target:
                shutil.move(source, target)
            rejected.append(f"{name}: firma discrepante")
            logging.error("RECHAZADO %s: firma discrepante", name)
            print(f"Rechazado: {name}")

    (ROOT / "output_samples" / "quarantine_manifest.txt").write_text(
        "\n".join(rejected) + ("\n" if rejected else ""), encoding="utf-8")


if __name__ == "__main__":
    main()
