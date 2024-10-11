import re
import pdfminer

from pdfminer.high_level import extract_text
import spacy
from spacy.matcher import Matcher
from fuzzywuzzy import fuzz, process


class ResumeParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = self.extract_text_from_pdf()

    def extract_text_from_pdf(self):
        try:
            return extract_text(self.pdf_path)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def extract_contact_number_from_resume(self, text):
        contact_number = None
        pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        match = re.search(pattern, text)
        if match:
            contact_number = match.group()
        return contact_number

    def extract_email_from_resume(self, text):
        email = None
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        match = re.search(pattern, text)
        if match:
            email = match.group()
        return email

    def extract_skills_from_resume(self, text, skills_list):
        skills = []
        for skill in skills_list:
            ratio = process.extractOne(skill, text, scorer=fuzz.token_sort_ratio)
            if ratio and ratio[1] >= 1:
                skills.append(skill)
        return skills

    def extract_education_from_resume(self, text):
        education = []
        pattern = r"(?i)(?:Bsc|\bB\.\w+|\bM\.\w+|\bPh\.D\.\w+|\bBachelor(?:'s)?|\bComputer(?:'s)?|\bPh\.D)\s(?:\w+\s)*\w+"
        matches = re.findall(pattern, text)
        for match in matches:
            education.append(match.strip())
        return education

    def extract_name(self, resume_text):
        nlp = spacy.load('en_core_web_sm')
        matcher = Matcher(nlp.vocab)
        patterns = [
            [{'POS': 'PROPN'}, {'POS': 'PROPN'}],
            [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],
            [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]
        ]
        for pattern in patterns:
            matcher.add('NAME', patterns=[pattern])
        doc = nlp(resume_text)
        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            return span.text
        return None


if __name__ == '__main__':
    resume_paths = r"C:/Users/User/Desktop/newCV.pdf"
    parser = ResumeParser(resume_paths)
    print("Resume: ", resume_paths)

    #Extract and print the name
    extract_name = parser.extract_name(parser.text)
    if extract_name:
        print("Name: ", extract_name)
    else:
        print("Name not found.")

    #Extract Contact Information
    contact_info = parser.extract_contact_number_from_resume(parser.text)
    if contact_info:
        print("Contact Number: ", contact_info)
    else:
        print("Contact Number not found")

    #Extracting Email
    email = parser.extract_email_from_resume(parser.text)
    if email:
        print("Email:", email)
    else:
        print("Email not found")
    skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management',
                   'Deep Learning', 'SQL', 'Tableau']
    extracted_skills = parser.extract_skills_from_resume(parser.text, skills_list)
    if extracted_skills:
        print("Skills:", extracted_skills)
    else:
        print("No skills found")
    extracted_education = parser.extract_education_from_resume(parser.text)
    if extracted_education:
        print("Education:", extracted_education)
    else:
        print("No education information found")
    print()
