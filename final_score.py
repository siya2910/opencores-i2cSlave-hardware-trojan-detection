from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


# Structural and LLM scores
STRUCTURAL_SCORE = 0.2112

# Qwen result for the current Trojan circuit:
# LOW = 0.2
# MEDIUM = 0.5
# HIGH = 0.9
LLM_RISK_SCORE = 0.5


# Fusion weight
# Structural contribution = 50%
# LLM semantic contribution = 50%
ALPHA = 0.50


def calculate_final_score(structural_score, llm_score):

    final_score = (
        ALPHA * structural_score
        + (1 - ALPHA) * llm_score
    )

    return final_score


def classify_risk(final_score):

    if final_score < 0.40:
        return "LOW"

    elif final_score < 0.70:
        return "MEDIUM"

    else:
        return "HIGH"


def main():

    final_score = calculate_final_score(
        STRUCTURAL_SCORE,
        LLM_RISK_SCORE
    )

    risk = classify_risk(final_score)

    print("\nHybrid Risk Assessment")
    print("----------------------")
    print(f"Structural Score : {STRUCTURAL_SCORE:.4f}")
    print(f"LLM Risk Score   : {LLM_RISK_SCORE:.4f}")
    print(f"Alpha            : {ALPHA:.2f}")
    print(f"Final Score      : {final_score:.4f}")
    print(f"Risk Level       : {risk}")


if __name__ == "__main__":
    main()