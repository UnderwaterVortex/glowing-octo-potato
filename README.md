# Indian Loan Document Tagger

A simple web-based tool built with Python and Streamlit to automatically classify and tag Indian secured loan documents (e.g., Sale Deed, PAN Card, Bank Statements) from uploaded PDF and image files.

-----

Features

  * Multi-File Upload: Accepts multiple PDF and image files (`.png`, `.jpg`, `.jpeg`).
  * OCR Text Extraction: Uses Tesseract-OCR to extract text from all documents.
  * Keyword-Based Classification: Automatically tags documents based on predefined keywords.
  * Application Summary: Provides a clear summary of which required documents are missing or duplicated.
  * Simple Web Interface: Built with Streamlit for ease of use.

-----

Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  Python 3.8+: [Download Python](https://www.python.org/downloads/)
2.  Tesseract-OCR: The optical character recognition engine.
      * Windows: Download from [Tesseract at UB Mannheim](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki).
      * macOS: `brew install tesseract`
3.  Poppler: A PDF rendering library.
      * Windows: Download the latest zip from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) and unzip it to a permanent location (e.g., `C:\poppler`).
      * macOS: `brew install poppler`

-----

 Setup & Installation

1.  Clone the repository (or download the `app.py` file):

    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  Create a `requirements.txt` file with the following content:

    ```txt
    streamlit
    pytesseract
    pdf2image
    Pillow
    pandas
    ```

3.  Install the Python libraries:

    ```bash
    pip install -r requirements.txt
    ```

4.  Configure Paths in `app.py` (For Windows Users):
    If you are on Windows, you must update `app.py` to point to your Tesseract and Poppler installations.

    ```python
    # For Windows, you must provide the exact paths.
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    POPPLER_PATH = r'C:\poppler\poppler-24.02.0-win-x86_64\bin' # Update this path to your Poppler 'bin' folder
    ```

    macOS users can usually leave these settings as they are in the final script.

-----

How to Run

1.  Open your terminal or command prompt.
2.  Navigate to the project directory.
3.  Run the following command:
    ```bash
    streamlit run app.py
    ```
4.  Your web browser will automatically open with the application running.

-----

 🔧 Tech Stack

  * Language: Python
  * Web Framework: Streamlit
  * OCR: Pytesseract
  * PDF Handling: pdf2image, Poppler
  * Image Handling: Pillow
  * Data Manipulation: Pandas

-----

Future Improvements

  * Improve Accuracy with Regex: Use regular expressions to find specific patterns (like PAN numbers or Aadhaar numbers) for more reliable classification.
  * Introduce Machine Learning: For higher accuracy, train a simple classifier model (e.g., Naive Bayes or a small transformer) on a labeled dataset of documents.
  * Add Caching: Implement Streamlit's caching decorators (`@st.cache_data`) to prevent reprocessing of the same file, speeding up the user experience.
