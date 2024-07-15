import pdfplumber
from transformers import pipeline

# Function to read text from a PDF file using pdfplumber
def read_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Initialize question generator once
question_generator = pipeline("text2text-generation", model="valhalla/t5-base-qg-hl")

# Function to generate unique questions using Hugging Face transformers
def generate_questions(input_text, num_questions=10):
    questions = []
    max_sequence_length = 512  # Maximum sequence length supported by the model
    chunk_size = max_sequence_length - 50  # Leave some buffer for safety
    
    # Process input_text in chunks
    while len(questions) < num_questions and input_text:
        chunk = input_text[:chunk_size]
        input_text = input_text[chunk_size:]
        
        # Generate a single question at a time due to limitations
        generated = question_generator(chunk, max_length=50, num_return_sequences=1)[0]['generated_text'].strip()
        questions.append(generated)
    
    return questions[:num_questions]

# Function to format the question paper
def format_question_paper(questions):
    question_paper = "Question Paper\n\n"
    for i, question in enumerate(questions, 1):
        question_paper += f"{i}. {question}\n"
    return question_paper

# Main function to generate the question paper
def main(file_path):
    try:
        # Read the input PDF file
        input_text = read_pdf(file_path)
        
        # Generate 10 unique questions using Hugging Face transformers
        questions = generate_questions(input_text, num_questions=10)
        
        # Format the question paper
        question_paper = format_question_paper(questions)
        
        # Save the question paper to a text file
        output_file = 'question_paper.txt'
        with open(output_file, 'w') as file:
            file.write(question_paper)
        
        # Print the confirmation message
        print(f"Question paper generated successfully and saved to '{output_file}'.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Replace '/content/input.pdf' with the path to your input PDF file
main('/content/input1.pdf')
