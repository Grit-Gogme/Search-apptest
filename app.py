import streamlit as st
from serpapi import GoogleSearch
from PyPDF2 import PdfReader
import requests
from transformers import pipeline

# Configuratie voor SerpAPI
SERPAPI_API_KEY = "487bd472e40f606b2e2a8ac48961981e5b4dfdab33590e5a31474de52bd74608"

# Initialiseer een samenvattingsmodel
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Functies
def fetch_google_scholar_results(query, num_results=10):
    """Haal de eerste 10 resultaten van Google Scholar op."""
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": num_results
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", [])

def download_pdf(url, filename):
    """Download een PDF van een URL."""
    response = requests.get(url)
    with open(filename, "wb") as file:
        file.write(response.content)

def extract_pdf_text(filepath):
    """Extracteer tekst uit een PDF-bestand."""
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Fout bij verwerken van PDF: {e}"

def analyze_text_deeply(text):
    """Diepere analyse van findings, implicaties en methoden."""
    # Gebruik een samenvattingsmodel
    findings = summarizer(text, max_length=100, min_length=30, do_sample=False)[0]["summary_text"]
    
    # Dummy logica voor specifieke secties (kan worden verbeterd met NLP-modellen)
    method_start = text.lower().find("method")
    implications_start = text.lower().find("implications")
    
    method_section = text[method_start:method_start + 500] if method_start != -1 else "Geen methoden gevonden."
    implications_section = text[implications_start:implications_start + 500] if implications_start != -1 else "Geen implicaties gevonden."
    
    return {
        "findings": findings,
        "methods": method_section,
        "implications": implications_section
    }

# Streamlit-interface
st.title("Google Scholar Artikel Analyzer")
st.write("Zoek naar artikelen, download PDF's en voer een diepere analyse uit.")

# Zoekbalk
search_query = st.text_input("Voer een zoekterm in:")
if st.button("Zoek"):
    results = fetch_google_scholar_results(search_query)
    
    for idx, result in enumerate(results[:10], start=1):
        title = result.get("title")
        link = result.get("link")
        pdf_link = result.get("resources", [{}])[0].get("link", link)  # PDF-link zoeken

        st.subheader(f"Artikel {idx}: {title}")
        st.write(f"[Link naar artikel]({link})")

        if pdf_link.endswith(".pdf"):
            st.write("PDF gevonden. Downloaden en analyseren...")
            pdf_filename = f"article_{idx}.pdf"
            download_pdf(pdf_link, pdf_filename)
            text = extract_pdf_text(pdf_filename)
            deep_analysis = analyze_text_deeply(text)
            
            st.write("### Findings")
            st.write(deep_analysis["findings"])
            st.write("### Onderzoeksmethoden")
            st.write(deep_analysis["methods"])
            st.write("### Praktische implicaties")
            st.write(deep_analysis["implications"])
        else:
            st.write("Geen PDF-link gevonden.")
