"""
Legality Service - Legal Rule Engine for Indian Law Compliance
Maps document types to specific Indian Laws/Guidelines and checks for violations.
"""
import json
import config
from services import key_manager


# ==================== LEGAL RULES DATABASE ====================
# Scalable dictionary mapping document types to Indian Laws
# Each rule has: law_name, description, source, keywords (for AI matching)

LEGAL_RULES = {
    "RENTAL": {
        "label": "Tenancy Law",
        "icon": "🏠",
        "rules": [
            {
                "id": "RENT_001",
                "rule_name": "Security Deposit Cap",
                "law_source": "Model Tenancy Act, 2021 – Section 8",
                "description": "Security Deposit for residential premises cannot exceed 2 months' rent.",
                "violation_text": "Deposit exceeding 2 months' rent",
                "keywords": ["security deposit", "advance deposit", "caution deposit", "refundable deposit"]
            },
            {
                "id": "RENT_002",
                "rule_name": "Eviction Notice Period",
                "law_source": "Model Tenancy Act, 2021 – Section 22",
                "description": "Landlord must provide at least 24 hours written notice before entering the premises for inspection.",
                "violation_text": "Entry without proper notice",
                "keywords": ["entry", "inspection", "access to premises", "landlord visit"]
            },
            {
                "id": "RENT_003",
                "rule_name": "Rent Increase Limit",
                "law_source": "Model Tenancy Act, 2021 – Section 9",
                "description": "Rent revision can only happen as per the agreement terms or by mutual consent, not exceeding once every year.",
                "violation_text": "Unrestricted rent escalation",
                "keywords": ["rent increase", "rent revision", "escalation", "rent hike"]
            },
            {
                "id": "RENT_004",
                "rule_name": "Lock-In Period",
                "law_source": "Indian Contract Act, 1872",
                "description": "A lock-in period clause that prevents the tenant from leaving even for genuine reasons may be considered unreasonable.",
                "violation_text": "Excessive lock-in period",
                "keywords": ["lock-in", "minimum stay", "cannot vacate", "lock in period"]
            },
            {
                "id": "RENT_005",
                "rule_name": "Maintenance Responsibility",
                "law_source": "Model Tenancy Act, 2021 – Section 15",
                "description": "Structural repairs and whitewashing are the landlord's responsibility. Only day-to-day maintenance falls on tenant.",
                "violation_text": "Unfair maintenance burden",
                "keywords": ["maintenance", "repair", "structural", "whitewashing", "painting"]
            }
        ]
    },
    "LOAN": {
        "label": "RBI / Banking Law",
        "icon": "🏦",
        "rules": [
            {
                "id": "LOAN_001",
                "rule_name": "Recovery Harassment Ban",
                "law_source": "RBI Fair Practices Code – Guidelines on Recovery Agents (2008)",
                "description": "Lenders cannot use muscle power, threats, or harassment for recovery. Recovery agents can only contact borrowers between 8 AM and 7 PM.",
                "violation_text": "Harassment-prone recovery terms",
                "keywords": ["recovery", "collection", "recovery agent", "default action", "repossession"]
            },
            {
                "id": "LOAN_002",
                "rule_name": "Foreclosure / Pre-Payment Penalty Ban",
                "law_source": "RBI Circular DNBR (PD) CC.No.054 / 03.10.119 / 2014-15",
                "description": "No foreclosure charges or pre-payment penalties are allowed on floating rate home loans for individual borrowers.",
                "violation_text": "Illegal pre-payment penalty",
                "keywords": ["foreclosure", "pre-payment", "prepayment penalty", "early closure", "pre-closure charges"]
            },
            {
                "id": "LOAN_003",
                "rule_name": "Excessive Interest Rate",
                "law_source": "RBI Master Direction on Interest Rate on Advances, 2016",
                "description": "Interest rates must be transparent and linked to a benchmark. Hidden charges or usurious rates violate RBI guidelines.",
                "violation_text": "Opaque or usurious interest",
                "keywords": ["interest rate", "hidden charges", "processing fee", "annual percentage rate"]
            },
            {
                "id": "LOAN_004",
                "rule_name": "Loan Agreement Transparency",
                "law_source": "RBI Fair Practices Code for Lenders",
                "description": "All terms including fees, penalties, and conditions must be clearly disclosed. Unilateral changes to loan terms are not permitted.",
                "violation_text": "Unilateral clause modification",
                "keywords": ["modify terms", "change conditions", "unilateral", "sole discretion", "amend terms"]
            },
            {
                "id": "LOAN_005",
                "rule_name": "EMI / Repayment Clarity",
                "law_source": "RBI Fair Practices Code",
                "description": "Lender must provide clear EMI schedule, breakup of principal and interest, and total cost of the loan upfront.",
                "violation_text": "Missing repayment transparency",
                "keywords": ["EMI", "repayment schedule", "installment", "principal", "amortization"]
            }
        ]
    },
    "EMPLOYMENT": {
        "label": "Labor Law",
        "icon": "💼",
        "rules": [
            {
                "id": "EMP_001",
                "rule_name": "Employment Bond Enforceability",
                "law_source": "Indian Contract Act, 1872 – Section 27 (Restraint of Trade)",
                "description": "Employment bonds demanding huge sums (e.g., ₹5 Lakhs) if an employee leaves are often legally unenforceable and considered 'bonded labor' if they exceed reasonable training costs.",
                "violation_text": "Excessive bond penalty",
                "keywords": ["bond", "training bond", "penalty for leaving", "bond amount", "service agreement bond"]
            },
            {
                "id": "EMP_002",
                "rule_name": "Notice Period Compensation",
                "law_source": "Industrial Disputes Act, 1947 – Section 25F",
                "description": "If an employer terminates immediately without cause, they must pay salary for the notice period. One month's notice or pay in lieu is standard.",
                "violation_text": "Missing notice period pay",
                "keywords": ["notice period", "termination", "immediate termination", "pay in lieu"]
            },
            {
                "id": "EMP_003",
                "rule_name": "Non-Compete Clause",
                "law_source": "Indian Contract Act, 1872 – Section 27",
                "description": "Post-employment non-compete clauses are generally void in India as they constitute 'restraint of trade'. Only limited garden leave clauses may be enforceable.",
                "violation_text": "Unenforceable non-compete",
                "keywords": ["non-compete", "non compete", "competitive restriction", "cannot join competitor"]
            },
            {
                "id": "EMP_004",
                "rule_name": "PF / Gratuity Compliance",
                "law_source": "Employees' Provident Funds Act, 1952 & Payment of Gratuity Act, 1972",
                "description": "Employers with 20+ employees must provide PF. Gratuity is payable after 5 years of continuous service. These are statutory rights and cannot be waived.",
                "violation_text": "Missing statutory benefits",
                "keywords": ["provident fund", "PF", "gratuity", "EPF", "statutory benefits"]
            },
            {
                "id": "EMP_005",
                "rule_name": "Working Hours & Overtime",
                "law_source": "Factories Act, 1948 & Shops and Establishments Act",
                "description": "No worker shall work more than 48 hours per week or 9 hours per day. Overtime must be paid at twice the ordinary rate.",
                "violation_text": "Excessive work hours without compensation",
                "keywords": ["working hours", "overtime", "extra hours", "work schedule", "weekly off"]
            }
        ]
    },
    "INSURANCE": {
        "label": "IRDAI Regulation",
        "icon": "🛡️",
        "rules": [
            {
                "id": "INS_001",
                "rule_name": "Free-Look Period",
                "law_source": "IRDAI (Protection of Policyholders' Interests) Regulations, 2017",
                "description": "Policyholder has a 15-day free-look period (30 days for e-policies) to return the policy and get a full refund if not satisfied.",
                "violation_text": "Missing free-look period",
                "keywords": ["free-look", "free look period", "cooling off", "return policy", "cancel policy"]
            },
            {
                "id": "INS_002",
                "rule_name": "Claim Settlement Timeline",
                "law_source": "IRDAI (Protection of Policyholders' Interests) Regulations, 2017",
                "description": "Insurance claims must be settled within 30 days of receiving all required documents. Delays attract 2% above bank rate as interest.",
                "violation_text": "No claim settlement guarantee",
                "keywords": ["claim settlement", "claim process", "claim timeline", "settlement period"]
            }
        ]
    },
    "NDA": {
        "label": "Contract Law",
        "icon": "🔒",
        "rules": [
            {
                "id": "NDA_001",
                "rule_name": "Reasonable Confidentiality Period",
                "law_source": "Indian Contract Act, 1872",
                "description": "Perpetual or excessively long confidentiality obligations (beyond 3-5 years) may be considered unreasonable and unenforceable.",
                "violation_text": "Excessive confidentiality period",
                "keywords": ["perpetual", "indefinite", "confidentiality period", "unlimited duration"]
            },
            {
                "id": "NDA_002",
                "rule_name": "One-Sided NDA Obligations",
                "law_source": "Indian Contract Act, 1872 – Section 16 (Undue Influence)",
                "description": "If the NDA places obligations only on one party with no reciprocity, it may be considered unconscionable.",
                "violation_text": "One-sided obligations",
                "keywords": ["one-sided", "unilateral", "receiving party only", "disclosing party rights"]
            }
        ]
    }
}

# ==================== DOCUMENT TYPE MAPPING ====================
# Maps AI-classified document types to our rule categories
DOCTYPE_TO_CATEGORY = {
    # Rental / Tenancy
    "Rent Agreement": "RENTAL",
    "Rental Agreement": "RENTAL",
    "Lease Agreement": "RENTAL",
    "Tenancy Agreement": "RENTAL",
    "Room Agreement": "RENTAL",
    "House Rent": "RENTAL",
    # Loan / Financial
    "Home Loan": "LOAN",
    "Loan Agreement": "LOAN",
    "Mortgage Agreement": "LOAN",
    "Personal Loan": "LOAN",
    "Car Loan": "LOAN",
    "Education Loan": "LOAN",
    "Credit Card Statement": "LOAN",
    "Bank Loan": "LOAN",
    # Employment
    "Employment Contract": "EMPLOYMENT",
    "Offer Letter": "EMPLOYMENT",
    "Appointment Letter": "EMPLOYMENT",
    "Service Agreement": "EMPLOYMENT",
    "Job Contract": "EMPLOYMENT",
    "Employment Agreement": "EMPLOYMENT",
    # Insurance
    "Insurance Policy": "INSURANCE",
    "Health Insurance": "INSURANCE",
    "Life Insurance": "INSURANCE",
    "Vehicle Insurance": "INSURANCE",
    "Motor Insurance": "INSURANCE",
    # NDA
    "NDA": "NDA",
    "Non-Disclosure Agreement": "NDA",
    "Confidentiality Agreement": "NDA",
}


def get_category_for_doctype(document_type):
    """Find the best matching legal category for a document type."""
    # Direct match
    if document_type in DOCTYPE_TO_CATEGORY:
        return DOCTYPE_TO_CATEGORY[document_type]
    
    # Fuzzy match based on keywords
    dt_lower = document_type.lower()
    if any(k in dt_lower for k in ["rent", "lease", "tenan"]):
        return "RENTAL"
    if any(k in dt_lower for k in ["loan", "mortgage", "credit", "bank", "finance"]):
        return "LOAN"
    if any(k in dt_lower for k in ["employ", "offer letter", "appointment", "job", "work contract"]):
        return "EMPLOYMENT"
    if any(k in dt_lower for k in ["insurance", "policy"]):
        return "INSURANCE"
    if any(k in dt_lower for k in ["nda", "non-disclosure", "confidential"]):
        return "NDA"
    
    return None


def check_legality(text, document_type, target_language='English'):
    """
    Run legality check on document text against Indian law rules.
    Uses AI to match clauses in the document against known legal rules.
    Returns list of violations with law sources.
    """
    category = get_category_for_doctype(document_type)
    
    if not category or category not in LEGAL_RULES:
        return {
            "category": None,
            "category_label": "General",
            "violations": [],
            "compliant_rules": [],
            "summary": "No specific Indian law rules configured for this document type.",
            "total_rules_checked": 0
        }
    
    rule_set = LEGAL_RULES[category]
    rules_for_prompt = "\n".join([
        f"Rule ID: {r['id']}\n"
        f"Rule: {r['rule_name']}\n"
        f"Law: {r['law_source']}\n"
        f"What to check: {r['description']}\n"
        f"Violation indicator: {r['violation_text']}\n"
        f"Keywords: {', '.join(r['keywords'])}\n"
        for r in rule_set['rules']
    ])

    prompt = f"""You are an Indian legal compliance auditor. Analyze this {document_type} document against specific Indian laws.

DOCUMENT TEXT:
{text[:15000]}

LEGAL RULES TO CHECK:
{rules_for_prompt}

For EACH rule above, check if the document violates it, complies with it, or if it's not applicable.

Respond in {target_language} using this EXACT JSON format:
{{
    "violations": [
        {{
            "rule_id": "RULE_ID",
            "rule_name": "Name of the rule",
            "law_source": "The exact law/act reference",
            "status": "VIOLATION",
            "severity": "HIGH",
            "clause_found": "The exact text from the document that violates this rule",
            "explanation": "Why this violates the law and what the legal position is",
            "recommendation": "What should be changed"
        }}
    ],
    "compliant_rules": [
        {{
            "rule_id": "RULE_ID",
            "rule_name": "Name of the rule", 
            "law_source": "The exact law/act reference",
            "status": "COMPLIANT",
            "note": "Brief note on how the document complies"
        }}
    ],
    "not_applicable": [
        {{
            "rule_id": "RULE_ID",
            "rule_name": "Name of the rule",
            "reason": "Why this rule doesn't apply to this document"
        }}
    ],
    "summary": "Overall legality summary of the document"
}}

Be thorough. Check every single rule. If a clause is ambiguous, flag it as a VIOLATION with severity MEDIUM.
Severity must be HIGH, MEDIUM, or LOW.
Respond with ONLY valid JSON:"""

    try:
        client = key_manager.get_openai_client()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert Indian legal compliance auditor specializing in {rule_set['label']}. Analyze documents against specific Indian laws. Respond in {target_language}. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=config.OPENAI_MODEL,
            temperature=0.2,
            max_tokens=4000
        )

        result = chat_completion.choices[0].message.content.strip()

        # Clean JSON
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        result = result.strip()

        data = json.loads(result)

        # Ensure required fields
        if 'violations' not in data:
            data['violations'] = []
        if 'compliant_rules' not in data:
            data['compliant_rules'] = []
        if 'not_applicable' not in data:
            data['not_applicable'] = []
        if 'summary' not in data:
            data['summary'] = ''

        # Add metadata
        data['category'] = category
        data['category_label'] = rule_set['label']
        data['category_icon'] = rule_set['icon']
        data['total_rules_checked'] = len(rule_set['rules'])

        return data

    except Exception as e:
        print(f"Error in legality check: {e}")
        return {
            "category": category,
            "category_label": rule_set['label'],
            "category_icon": rule_set['icon'],
            "violations": [],
            "compliant_rules": [],
            "not_applicable": [],
            "summary": "Error performing legality check. Please try again.",
            "total_rules_checked": len(rule_set['rules']),
            "error": str(e)
        }
