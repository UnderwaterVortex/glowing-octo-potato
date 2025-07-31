# Import all the libraries we installed. Think of this as grabbing our tools.
import streamlit as st
import pytesseract
from pdf2image import convert_from_path
import tempfile
import pandas as pd
from PIL import Image

# --- IMPORTANT CONFIGURATION ---
# This tells our script where to find the helper tools.
#
# If you are on macOS and used Homebrew, these can be left as they are.
# If you are on Windows, you MUST update these paths to where you installed the tools.

# For Windows Users: Uncomment the line below and update the path to your Tesseract installation.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# For Windows Users: Update this path to the 'bin' folder inside your unzipped Poppler directory.
# For macOS Users: Leave this as None.
POPPLER_PATH = None

# --------------------------------------------------------

# This is the "brain" of our classifier.
# It defines document types and the keywords to look for.
DOCUMENT_KEYWORDS = {
    "Sale Deed": ["sale deed", "deed of sale", "stamp duty", "consideration amount", "vendor", "vendee"],
    "PAN Card": ["permanent account number", "pan card", "income tax department"],
    "Aadhaar Card": ["aadhaar", "unique identification authority", "uidai"],
    "Bank Statement": ["bank statement", "account number", "transaction date", "closing balance"],
    "Income Tax Return (ITR)": ["income tax return", "acknowledgement", "itr-v", "assessment year"],
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


@st.cache_data
def extract_text_from_pdf(pdf_file):
    """
    This function takes an uploaded PDF, converts its first few pages to images,
    and uses Tesseract to extract text. Caching improves performance.
    """
    text = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_file.getvalue())
            temp_pdf_path = temp_pdf.name

        # Process only the first 2 pages for speed.
        images = convert_from_path(temp_pdf_path, poppler_path=POPPLER_PATH, last_page=2)

        for img in images:
            text += pytesseract.image_to_string(img) + "\n"

    except Exception as e:
        st.error(f"Error processing PDF {pdf_file.name}: {e}")
        return ""

    return text.lower()


@st.cache_data
def extract_text_from_image(image_file):
    """
    This function takes an uploaded image file, opens it, and uses Tesseract
    to extract text. Caching improves performance.
    """
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text.lower()
    except Exception as e:
        st.error(f"Error processing image {image_file.name}: {e}")
        return ""


def classify_document(text):
    """
    This function checks the extracted text for our keywords
    and returns the document type it thinks it is.
    """
    for doc_type, keywords in DOCUMENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return doc_type
    return "Unclassified"


# --- Building the Web Interface with Streamlit ---

st.set_page_config(page_title="Indian Loan Document Tagger", layout="wide")

st.title("📄 Indian Secured Loan Document Tagger")
st.write("Upload your loan documents (PDFs and images) and this tool will automatically tag them for you.")

uploaded_files = st.file_uploader(
    "Choose PDF or Image files",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Processing {len(uploaded_files)} files... Please wait.")

    results = []

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name.lower()
        extracted_text = ""

        if file_name.endswith('.pdf'):
            extracted_text = extract_text_from_pdf(uploaded_file)
        elif file_name.endswith(('.png', '.jpg', '.jpeg')):
            extracted_text = extract_text_from_image(uploaded_file)

        if extracted_text:
            doc_type = classify_document(extracted_text)
            results.append({"Filename": uploaded_file.name, "Detected Type": doc_type})
        else:
            # Append even if there's an error to show the filename in the table
            results.append({"Filename": uploaded_file.name, "Detected Type": "Error during processing"})

    st.header("✅ Processing Complete!")
    result_df = pd.DataFrame(results)
    st.dataframe(result_df, use_container_width=True)

    st.header("📊 Application Summary")

    detected_types = result_df["Detected Type"].tolist()

    missing_docs = [doc for doc in REQUIRED_DOCS if doc not in detected_types]
    if missing_docs:
        st.warning(f"**Missing Documents:** {', '.join(missing_docs)}")
    else:
        st.success("All required documents are present!")

    found_docs = [doc for doc in detected_types if doc not in ["Unclassified", "Error during processing"]]
    duplicates = [doc for doc in set(found_docs) if found_docs.count(doc) > 1]
    if duplicates:
        st.error(f"**Duplicate Documents Found:** {', '.join(duplicates)}")
    else:
        st.success("No duplicate documents found.")
