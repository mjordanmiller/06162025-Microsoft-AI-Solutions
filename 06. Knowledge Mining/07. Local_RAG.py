from create_responses import get_information
import os
from dotenv import load_dotenv
import json
import re
import pprint

#load environment variables
load_dotenv()

openai_endpoint = os.getenv('AI_OPENAI_ENDPOINT')
openai_key = os.getenv('AI_OPENAI_KEY')


questions = [
    "What are the details for the subcontractor agreement (including the contract number, funding amount, funding start date, and funding end date)?",
    "Is there any indication in the contract about when a new SOW should be requested?",
    "List all ATPs categorized by SOW, including funded and unfunded ATP amounts.",
    "What are the labor categories and associated bill rates in the contract?",
    "For each labor category, are there any bill rate increases over time? Include the effective dates and new rates.",
    "What are the pay rates for each labor category?",
    "Who is the individual the contract is written for? Provide their full legal name.",
    "Who is the prime contractor or customer in this agreement (e.g., MBO Partners)?",
    "Who is the end client (e.g., IRS or another government agency)?",
    "Who is the deal economic buyer for escalation purposes? Include their name, email, and phone number.",
    "Who is the accounts payable contact? Include their name, email, and phone number."
]

question_formats = [
    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "contractNumber": "_____",
            "funding": {
                "amount": _____,
                "startDate": "_____",
                "endDate": "_____"
            }
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "newSowIndicator": "_____"
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "atp": [
                {
                    "funded": _____,
                    "unfunded": _____
                }
            ]
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "laborCategories": [
                {
                    "laborCategory": "_____",
                    "billRate": _____
                }
            ]
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "laborCategories": [
                {
                    "laborCategory": "_____",
                    "optionYear": [
                        {
                            "newRate": _____,
                            "effectiveDate": "_____"
                        }
                    ]
                }
            ]
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "laborCategories": [
                {
                    "laborCategory": "_____",
                    "payRate": _____
                }
            ]
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "individualName": "_____"
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "primeContractor": "_____"
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "endClient": "_____"
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "economicBuyerContact": {
                "name": "_____",
                "email": "_____",
                "phone": "_____"
            }
        }
    }''',

    '''Provide the output in the following JSON format:
    {"subcontractorAgreement": 
        {
            "accountsPayableContact": {
                "name": "_____",
                "email": "_____",
                "phone": "_____"
            }
        }
    }'''
]


#Playing with system messages
system_message = '''
                    You are an assistant that tries to get information out of text.
                    Answer the question using only the sources provided below.
                    Answer ONLY with the facts listed in the provided text.
                    Do not repeat the question to me, just provide the answer in a concise way.
                    If there isn't enough information below, say you don't know.
                    Do not generate answers that don't use the sources below.
                    '''

results = get_information(questions=questions,
                          question_formats=question_formats,
                          openai_endpoint=openai_endpoint,
                          openai_key=openai_key,
                          system_message=system_message,
                          document_fpath="./Data/testContract1.pdf",
                          collection_name="pdf_vectors")



combined = {}

for _, answer in results:
    # Remove markdown formatting like ```json
    cleaned = re.sub(r"```json|```", "", answer).strip()
    try:
        parsed = json.loads(cleaned)
        if "subcontractorAgreement" in parsed:
            # Merge preserving nested structure
            for key, value in parsed["subcontractorAgreement"].items():
                # Overwrite on key collision (custom merge logic can go here)
                combined[key] = value
        else:
            print("Warning: 'subcontractorAgreement' key not found in parsed result.")
    except json.JSONDecodeError as e:
        print(f"Error parsing:\n{cleaned}\n{e}")



pprint.pprint(combined)