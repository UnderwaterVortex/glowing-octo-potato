# Import all the libraries we installed. Think of this as grabbing our tools.
import streamlit as st
import pytesseract
from pdf2image import convert_from_path
import tempfile
import pandas as pd
from PIL import Image

# --- IMPORTANT CONFIGURATION ---
# This tells our script where to find the tools we installed in Part 1.
#
# For Windows Users:
# 1. Update the tesseract_cmd path to where you installed Tesseract-OCR.
#    Common path: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# 2. Update the poppler_path to the 'bin' folder you created.
#    Common path: r'C:\poppler\poppler-24.02.0-win-x86_64\bin'
#
# For macOS/Linux Users:
# You can usually leave these commented out, as the system often finds them automatically.
# If it doesn't work, you might need to find the paths and add them.

# --- !! UPDATE THESE PATHS IF YOU ARE ON WINDOWS !! ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = None  # UPDATE THIS PATH
# --------------------------------------------------------

# This is the "brain" of our classifier.
# We define document types and the keywords to look for in each document.
# The more specific the keywords, the better the classification.
DOCUMENT_KEYWORDS = {
    "Sale Deed": ["sale deed", "deed of sale", "stamp duty", "consideration amount", "vendor", "vendee"],
    "PAN Card": ["permanent account number", "pan card", "income tax department","pan"],
    "Aadhaar Card": ["aadhaar", "unique identification authority", "uidai","uid"],
    "Bank Statement": ["bank statement", "account number", "transaction date", "closing balance"],
    "Income Tax Return (ITR)": ["income tax return", "acknowledgement", "itr-v", "assessment year","itr"],
    "Salary Slip": ["salary slip", "payslip", "earnings", "deductions", "net pay"],
    "Legal Scrutiny Report": ["legal scrutiny report", "title search report", "advocate", "legal opinion"],
    "No Objection Certificate (NOC)": ["no objection certificate", "noc", "no objection"],
}

# These are the documents we expect for a complete loan application.
REQUIRED_DOCS = [
    "Sale Deed",
    "PAN Card",
    "Aadhaar Card",
    "Bank Statement",
    "Income Tax Return (ITR)",
    "Legal Scrutiny Report"
]


def extract_text_from_pdf(pdf_file):
    """
    This function takes an uploaded PDF file, saves it temporarily,
    converts it to images, and uses Tesseract to extract text.
    """
    text = ""
    try:
        # Save the uploaded file to a temporary location on your computer
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_file.getvalue())
            temp_pdf_path = temp_pdf.name

        # For Windows, we need to provide our poppler_path
        # For macOS/Linux, it's often found automatically (poppler_path=None)
        images = convert_from_path(temp_pdf_path, poppler_path=POPPLER_PATH)

        # "Read" the text from each image (page) using Tesseract
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"

    except Exception as e:
        # If anything goes wrong, we'll show an error.
        st.error(f"Error processing {pdf_file.name}: {e}")
        return ""

    return text.lower()  # Return text in lowercase for easier keyword matching


def classify_document(text):
    """
    This function checks the extracted text for our keywords
    and returns the document type it thinks it is.
    """
    for doc_type, keywords in DOCUMENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return doc_type  # Found a match!
    return "Unclassified"  # If no keywords are found


# --- Building the Web Interface with Streamlit ---

st.set_page_config(page_title="Indian Loan Document Tagger", layout="wide")

st.title("📄 Indian Secured Loan Document Tagger")
st.write("Upload your loan documents (PDFs only) and this tool will automatically tag them for you.")

# Create the file uploader
uploaded_files = st.file_uploader(
    "Choose PDF files",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    # If files are uploaded, start processing
    st.info(f"Processing {len(uploaded_files)} files... Please wait.")

    results = []

    # Go through each uploaded file one by one
    for uploaded_file in uploaded_files:
        # Step 1: Extract text
        extracted_text = extract_text_from_pdf(uploaded_file)

        # Step 2: Classify the document based on the text
        if extracted_text:
            doc_type = classify_document(extracted_text)
            results.append({"Filename": uploaded_file.name, "Detected Type": doc_type})
        else:
            results.append({"Filename": uploaded_file.name, "Detected Type": "Error during processing"})

    # Display the results in a neat table
    st.header("✅ Processing Complete!")
    result_df = pd.DataFrame(results)
    st.dataframe(result_df, use_container_width=True)

    # --- Summary Section: Check for Missing and Duplicate Docs ---
    st.header("📊 Application Summary")

    detected_types = result_df["Detected Type"].tolist()

    # Find missing documents
    missing_docs = [doc for doc in REQUIRED_DOCS if doc not in detected_types]
    if missing_docs:
        st.warning(f"**Missing Documents:** {', '.join(missing_docs)}")
    else:
        st.success("All required documents are present!")

    # Find duplicate documents
    found_docs = [doc for doc in detected_types if doc != "Unclassified" and doc != "Error during processing"]
    duplicates = [doc for doc in set(found_docs) if found_docs.count(doc) > 1]
    if duplicates:
        st.error(f"**Duplicate Documents Found:** {', '.join(duplicates)}")
    else:
        st.success("No duplicate documents found.")
