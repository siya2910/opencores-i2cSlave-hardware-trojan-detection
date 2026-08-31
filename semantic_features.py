import re
import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

RTL_FILES = [
    BASE_DIR / "clean" / "i2cSlave.v",
    BASE_DIR / "clean" / "i2cSlaveTop.v",
    BASE_DIR / "clean" / "i2cSlave_define.v",
    BASE_DIR / "clean" / "registerInterface.v",
    BASE_DIR / "clean" / "serialInterface.v",
]

OUTPUT_FILE = BASE_DIR / "results" / "i2cSlave_semantic_features.csv"


def read_rtl():
    text = ""

    for file in RTL_FILES:
        if file.exists():
            with open(file, "r", errors="ignore") as f:
                text += "\n" + f.read()

    return text


def count_pattern(text, pattern):
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def extract_features(text):

    features = {}

    # References to trigger/payload terminology
    features["TriggerRefs"] = count_pattern(
        text,
        r"\b(trigger|startEdgeDet|startStopDet)\b"
    )

    features["PayloadRefs"] = count_pattern(
    text,
    r"clean_myReg0\s*\^\s*8'hFF"
    )

    # Counter-related structures
    features["TriggerCounter"] = count_pattern(
        text,
        r"\b(counter|count)\b"
    )

    # Rare constants / comparison constants
    equality_checks = count_pattern(
        text,
        r"==|!="
    )

    features["RareTriggerConstant"] = 1 if equality_checks > 0 else 0

    # Multiple signal conditions
    multi_signal = count_pattern(
        text,
        r"&&|\|\|"
    )

    features["MultiSignalTrigger"] = 1 if multi_signal > 0 else 0

    # FSM/state-related structures
    fsm_count = count_pattern(
        text,
        r"\b(state|fsm|case)\b"
    )

    features["FSMTrigger"] = 1 if fsm_count > 0 else 0

    # Address-dependent logic
    address_count = count_pattern(
        text,
        r"\b(addr|address|regAddr)\b"
    )

    features["AddressTrigger"] = 1 if address_count > 0 else 0

    # Instruction-dependent logic
    instruction_count = count_pattern(
        text,
        r"\b(instruction|opcode|instructionCode)\b"
    )

    features["InstructionTrigger"] = 1 if instruction_count > 0 else 0

    # Comparators
    features["Comparators"] = equality_checks

    # Registers
    features["Registers"] = count_pattern(
        text,
        r"\breg\b|\bregister\b"
    )

    return features


def save_features(features):

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=features.keys()
        )

        writer.writeheader()
        writer.writerow(features)


def main():

    print("Reading OpenCores RTL...")

    rtl = read_rtl()

    if not rtl:
        raise FileNotFoundError(
            "No RTL files found."
        )

    features = extract_features(rtl)
    
    # Semantic suspicion score as defined in the paper
    trigger_counter = features.get("TriggerCounter", 0)
    rare_trigger = features.get("RareTriggerConstant", 0)
    trigger_refs = features.get("TriggerRefs", 0)
    payload_refs = features.get("PayloadRefs", 0)
    
    semantic_score = (
                      2 * trigger_counter
                    + 2 * rare_trigger
                    + min(trigger_refs, 4)
                    + min(payload_refs, 4)
                      )
    
    print(f"SemanticScore: {semantic_score}")
    print("\nSemantic Features")
    print("-----------------")

    for key, value in features.items():
        print(f"{key}: {value}")

    save_features(features)

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()