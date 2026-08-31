import csv
import json
import requests
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

STRUCTURAL_FILE = RESULTS_DIR / "i2cSlave_structural_features.csv"
SEMANTIC_FILE = RESULTS_DIR / "i2cSlave_semantic_features.csv"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:7b"


def read_csv(filename):
    with open(filename, "r", newline="") as f:
        return next(csv.DictReader(f))


def build_prompt(structural, semantic):

    semantic_score = (
        2 * int(semantic["TriggerCounter"])
        + 2 * int(semantic["RareTriggerConstant"])
        + min(int(semantic["TriggerRefs"]), 4)
        + min(int(semantic["PayloadRefs"]), 4)
    )

    prompt = f"""
You are a hardware security analyst evaluating an RTL circuit
for possible Hardware Trojan activity.

The circuit is an OpenCores i2cSlave design.

IMPORTANT:
Do not classify a circuit as malicious merely because it contains
FSMs, registers, comparators, address logic, or multi-signal conditions.
These can be legitimate components of an I2C controller.

However, explicit combinations of:
- rare activation conditions,
- counter-based activation,
- additional trigger logic,
- payload/output manipulation,
- and security-invariant violations

should be treated as strong evidence of a Hardware Trojan.

Current Circuit Features
------------------------
Nodes = {structural["Nodes"]}
Edges = {structural["Edges"]}
AverageDegree = {structural["AverageDegree"]}
RareNodeCount = {structural["RareNodeCount"]}
StructuralScore = {structural["StructuralScore"]}

Semantic Features
-----------------
TriggerRefs = {semantic["TriggerRefs"]}
PayloadRefs = {semantic["PayloadRefs"]}
TriggerCounter = {semantic["TriggerCounter"]}
RareTriggerConstant = {semantic["RareTriggerConstant"]}
MultiSignalTrigger = {semantic["MultiSignalTrigger"]}
FSMTrigger = {semantic["FSMTrigger"]}
AddressTrigger = {semantic["AddressTrigger"]}
InstructionTrigger = {semantic["InstructionTrigger"]}
Comparators = {semantic["Comparators"]}
Registers = {semantic["Registers"]}

SemanticScore = {semantic_score}

Security Invariants
-------------------
1. Counter logic should not activate hidden payload functionality.
2. Rare activation conditions should not trigger malicious logic.
3. Trigger logic should have a legitimate functional purpose.
4. Payload-like output manipulation should be consistent with the
   intended circuit functionality.

Analysis Guidance
-----------------
A clean reference I2C design has:
Nodes = 207
Edges = 421
SemanticScore = 6
TriggerCounter = 0
PayloadRefs = 0

The current circuit has the features listed above.

Compare the current circuit with the clean reference.
Pay particular attention to additional logic and the combination
of trigger and payload indicators.

Do not treat a hypothetical possibility as an actual invariant
violation. Base the decision on the observed features.

Determine whether the current circuit contains evidence of a
Hardware Trojan.

Return ONLY valid JSON in this format:

{{
  "risk_level": "LOW | MEDIUM | HIGH",
  "confidence": 0,
  "trigger_interpretation": "",
  "payload_interpretation": "",
  "invariant_violations": [],
  "reason": ""
}}

Confidence must be an integer from 0 to 100.
"""

    return prompt


def run_llm(prompt):

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=300
    )

    response.raise_for_status()

    return response.json()["response"]


def main():

    print("Loading structural features...")
    structural = read_csv(STRUCTURAL_FILE)

    print("Loading semantic features...")
    semantic = read_csv(SEMANTIC_FILE)

    prompt = build_prompt(structural, semantic)

    print("\nSending circuit description to Qwen...")

    result = run_llm(prompt)

    print("\nLLM Response")
    print("------------")
    print(result)


if __name__ == "__main__":
    main()