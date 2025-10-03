"""
Main Runner Script for Paper Search Backend
This is the entry point for using the backend with your own input
"""

import json
from main import PaperSearchBackend
from config import GEMINI_API_KEY, FORMAT_REFERENCE_FILE, OUTPUT_FILE


def process_single_input(input_data: dict):
    """
    Process a single input and display results
    
    Args:
        input_data: Dictionary containing the paper search input
    """
    print("\n" + "="*80)
    print("PROCESSING INPUT")
    print("="*80)
    
    # Initialize backend
    backend = PaperSearchBackend(GEMINI_API_KEY)
    
    # Display input
    print("\nINPUT DATA:")
    print("-"*80)
    print(json.dumps(input_data, indent=2))
    
    # Process input
    refined_output = backend.process_input(input_data, FORMAT_REFERENCE_FILE)
    
    # Display output
    print("\n" + "="*80)
    print("REFINED OUTPUT (in required format)")
    print("="*80)
    print(json.dumps(refined_output, indent=2))
    
    # Show changes
    print("\n" + "="*80)
    print("CHANGES SUMMARY")
    print("="*80)
    print(f"Subject Area: {input_data.get('subjectArea')} → {refined_output.get('subjectArea')}")
    print(f"Keywords Extracted: {len(refined_output.get('keywords', []))} keywords")
    print(f"Open Access: {input_data.get('openAccess')} → {refined_output.get('openAccess')}")
    
    # Save output
    with open(OUTPUT_FILE, "w") as f:
        json.dump(refined_output, f, indent=2)
    
    print("\n" + "="*80)
    print(f"✓ Output saved to: {OUTPUT_FILE}")
    print("="*80)
    
    return refined_output


def get_user_input():
    """
    Get input from user interactively
    
    Returns:
        Dictionary containing the user's input
    """
    print("\n" + "="*80)
    print("PAPER SEARCH BACKEND - INPUT CONFIGURATION")
    print("="*80)
    print("\nPlease enter the following details:\n")
    
    # Get subject area
    subject_area = input("Subject Area (e.g., DL, AI, ML, CV): ").strip()
    
    # Get title
    print("\nPaper Title:")
    title = input("> ").strip()
    
    # Get abstract
    print("\nPaper Abstract (press Enter twice when done):")
    print("> ", end="")
    abstract_lines = []
    while True:
        line = input()
        if line == "":
            break
        abstract_lines.append(line)
    abstract = " ".join(abstract_lines).strip()
    
    # Get acceptance percentage range
    while True:
        try:
            acc_from = int(input("\nAcceptance Percentage From (0-100): ").strip())
            if 0 <= acc_from <= 100:
                break
            print("Please enter a value between 0 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            acc_to = int(input("Acceptance Percentage To (0-100): ").strip())
            if 0 <= acc_to <= 100 and acc_to >= acc_from:
                break
            if acc_to < acc_from:
                print("'To' value must be greater than or equal to 'From' value")
            else:
                print("Please enter a value between 0 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    # Get open access preference
    while True:
        open_access = input("\nOpen Access (yes/any): ").strip().lower()
        if open_access in ['yes', 'any']:
            break
        print("Please enter 'yes' or 'any'")
    
    # Build input data
    input_data = {
        "subjectArea": subject_area,
        "title": title,
        "abstract": abstract,
        "accPercentFrom": acc_from,
        "accPercentTo": acc_to,
        "openAccess": open_access
    }
    
    return input_data


def main():
    """
    Main function - Gets input from user interactively
    """
    print("\n" + "="*80)
    print("WELCOME TO PAPER SEARCH BACKEND")
    print("="*80)
    
    # Directly get input from user
    input_data = get_user_input()
    
    # Process the input
    process_single_input(input_data)


# Example alternative inputs (uncomment to use):

def example_1():
    """Computer Vision Example"""
    input_data = {
        "subjectArea": "CV and DL",
        "title": "CNN Architectures for Real-Time Object Detection",
        "abstract": "We explore CNN and RNN for CV tasks with GPU accelaration for real-time procesing.",
        "accPercentFrom": 30,
        "accPercentTo": 50,
        "openAccess": True
    }
    process_single_input(input_data)


def example_2():
    """NLP Chatbot Example"""
    input_data = {
        "subjectArea": "NLP and AI",
        "title": "Enhancing Chatbot Performence Through Advanced NLU",
        "abstract": "This reasearch focusses on improving chatbot performence using transformr models like BERT and GPT.",
        "accPercentFrom": 25,
        "accPercentTo": 45,
        "openAccess": "yes"
    }
    process_single_input(input_data)


def example_3():
    """Reinforcement Learning Example"""
    input_data = {
        "subjectArea": "RL and AI",
        "title": "RL Agents for Complex Task Planning",
        "abstract": "We develop RL agents using deep Q-networks and policy gradient methods for multi-agent environments.",
        "accPercentFrom": 40,
        "accPercentTo": 60,
        "openAccess": 1
    }
    process_single_input(input_data)


def load_from_json_file(filepath: str):
    """
    Load input from a JSON file and process it
    
    Args:
        filepath: Path to the JSON file containing input data
    """
    try:
        with open(filepath, 'r') as f:
            input_data = json.load(f)
        process_single_input(input_data)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{filepath}'")


if __name__ == "__main__":
    # Run the main function with the configured input
    main()
    
    # Uncomment any of these to run specific examples:
    # example_1()
    # example_2()
    # example_3()
    
    # Uncomment to load from a JSON file:
    # load_from_json_file("my_input.json")
