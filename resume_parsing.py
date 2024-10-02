import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import docx
import spacy
from spacy.matcher import Matcher
import re


# Improved error handling and user feedback
def parse_resume(resume_text):
    """Parses a resume and extracts key information.

    Args:
        resume_text (str): The text content of the resume.

    Returns:
        dict: A dictionary containing the extracted information,
              or None if parsing fails.
    """
    try:
        nlp = spacy.load("en_core_web_sm")  # Load smaller model for performance

        # Define patterns for various sections
        doc = nlp(resume_text)
        matcher = Matcher(nlp.vocab)

        # Patterns for name, contact, email, experience, and skills
        name_patterns = [{"LOWER": "abdulsamod"}, {"LOWER": "azeez"}]
        matcher.add("NAME", [name_patterns])

        parsed_data = {"name": None, "contact": None, "email": None, "experience": None, "skills": None}
        matches = matcher(doc)

        for match_id, start, end in matches:
            matched_span = doc[start:end]
            match_id_str = nlp.vocab.strings[match_id]
            if match_id_str == "NAME":
                parsed_data["name"] = matched_span.text.strip()

        # Extract phone numbers using regex
        phone_numbers = re.findall(r'\(\+\d{1,3}\) \d{3} \d{3} \d{4}', resume_text)
        if phone_numbers:
            parsed_data["contact"] = phone_numbers[0]

        # Extract emails using regex
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
        if emails:
            parsed_data["email"] = emails[0]

        # Extract experience and skills sections manually
        experience_match = re.search(
            r'WORK EXPERIENCE(.*?)(EDUCATION|ADDITIONAL EXPERIENCE|PUBLICATIONS|CONFERENCES|LANGUAGES)', resume_text,
            re.DOTALL | re.IGNORECASE)
        skills_match = re.search(
            r'TECHNICAL PROFICIENCIES(.*?)(WORK EXPERIENCE|EDUCATION|ADDITIONAL EXPERIENCE|PUBLICATIONS|CONFERENCES|LANGUAGES)',
            resume_text, re.DOTALL | re.IGNORECASE)

        if experience_match:
            parsed_data["experience"] = experience_match.group(1).strip()
        if skills_match:
            parsed_data["skills"] = skills_match.group(1).strip()

        return parsed_data

    except Exception as e:
        st.error(f"Error parsing resume: {e}")
        return None


def read_pdf(file):
    """Extracts text from a PDF file."""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def read_docx(file):
    """Extracts text from a DOCX file."""
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def main():
    """
    Streamlit app to handle multiple resume parsing and display results in a table.
    """

    st.title("Resume Parser")
    st.subheader("Upload multiple resumes (PDF, DOC, or text format)")

    # Improved file upload handling and feedback
    uploaded_files = st.file_uploader("Choose your resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    if uploaded_files:
        parsed_resumes = []
        for uploaded_file in uploaded_files:
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                resume_text = read_pdf(uploaded_file)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = read_docx(uploaded_file)
            elif file_type == "text/plain":
                resume_text = uploaded_file.read().decode("utf-8")
            else:
                st.warning(f"Unsupported file type: {file_type}")
                continue

            parsed_data = parse_resume(resume_text)
            if parsed_data:
                parsed_resumes.append(parsed_data)
            else:
                st.warning(f"Failed to parse resume: {uploaded_file.name}")

        if parsed_resumes:
            df = pd.DataFrame(parsed_resumes)
            st.dataframe(df)


if __name__ == "__main__":
    main()
