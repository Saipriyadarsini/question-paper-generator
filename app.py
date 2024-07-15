from flask import Flask, request, send_file, jsonify, Response
import pdfplumber
from transformers import pipeline
import os
from fpdf import FPDF
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

# Function to create PDF from text
def create_pdf(text, output_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)
    pdf.output(output_file)

# Route to handle file upload and PDF generation
@app.route('/generate', methods=['POST'])
def generate():
    uploaded_file = request.files['file']
    
    if uploaded_file.filename != '':
        file_path = os.path.join("uploads", uploaded_file.filename)
        uploaded_file.save(file_path)
        
        # Generate question paper
        input_text = read_pdf(file_path)
        questions = generate_questions(input_text)
        question_paper = format_question_paper(questions)
        
        # Save question paper to a PDF file
        output_file = os.path.join("outputs", "question_paper.pdf")
        create_pdf(question_paper, output_file)
        
        # Send file for download
        with open(output_file, 'rb') as f:
            response = Response(f.read(), mimetype='application/pdf')
            response.headers['Content-Disposition'] = 'attachment; filename=question_paper.pdf'
            return response
    
    return jsonify({"error": "No file uploaded"}), 400

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    app.run(debug=True)
