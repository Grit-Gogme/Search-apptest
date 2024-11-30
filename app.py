import streamlit as st
from serpapi import GoogleSearch
from PyPDF2 import PdfReader
import requests

# Configuratie voor SerpAPI
SERPAPI_API_KEY = "jouw_serpapi_api_sleutel"

# Functies
def fetch_google_scholar_results(query, num_results=10):
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
    response = requests.get(url)
    with open(filename, "wb") as file:
        file.write(response.content)

def extract_pdf_text(filepath):
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Fout bij verwerken van PDF: {e}"

def analyze_text(text):
    word_count = len(text.split())
    summary = text[:500] + "..."  # Eenvoudige samenvatting
    return {"word_count": word_count, "summary": summary}

# Streamlit-interface
st.title("Google Scholar Artikel Analyzer")
search_query = st.text_input("Voer een zoekterm in:")
if st.button("Zoek"):
    results = fetch_google_scholar_results(search_query)
    for idx, result in enumerate(results[:10], start=1):
        title = result.get("title")
        link = result.get("link")
        pdf_link = result.get("resources", [{}])[0].get("link", link)

        st.subheader(f"Artikel {idx}: {title}")
        st.write(f"[Link naar artikel]({link})")

        if pdf_link.endswith(".pdf"):
            st.write("PDF gevonden. Analyseren...")
            pdf_filename = f"article_{idx}.pdf"
            download_pdf(pdf_link, pdf_filename)
            text = extract_pdf_text(pdf_filename)
            analysis = analyze_text(text)
            st.write(f"Woordaantal: {analysis['word_count']}")
            st.write(f"Samenvatting: {analysis['summary']}")
        else:
            st.write("Geen PDF gevonden.")
