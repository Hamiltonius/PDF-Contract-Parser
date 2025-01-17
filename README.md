
# PDF Contract Detail Scraper

# Overview
The PDF Contract Detail Scraper is a Python-based tool designed to extract relevant contract information from PDF files and assemble the details into a structured format, such as an Excel file. This tool automates the extraction of essential contract fields (e.g., Contract ID, Period of Performance, CLIN Description, etc.), reducing manual effort and improving accuracy in managing contract data.



# Features

Automated PDF Scanning: Reads through PDF files and extracts specific contract information using regex patterns.

Flexible Data Extraction: Extracts details like Contract ID, Period of Performance, Contract Value, CLIN Descriptions, and more.

Structured Output: Outputs the extracted data into a well-formatted Excel file for further analysis or reporting.

Error Handling: Includes basic error handling to account for missing or incomplete fields in the PDF files.


# Technologies Used:


Python 3.12

PyPDF2: A library used to extract text from PDF files.

pandas: A powerful data manipulation and analysis library used to structure extracted data and export it to Excel.

re: Regular expression library used for pattern matching to extract specific details from the PDF text.

Installation:
python -m venv venv
source venv/bin/activate  # For Linux/macOS
.\venv\Scripts\activate   # For Windows



TL:DR

This tool automates the extraction of contract details from PDF files and converts them into structured formats (Excel/CSV) using Python and pandas.

# Setup Instructions: 

Install dependencies and run the script.

### Create a virtual environment
python -m venv venv

### Activate the virtual environment
source venv/bin/activate  # For Linux/macOS
.\venv\Scripts\activate   # For Windows

### Install the dependencies
pip install -r requirements.txt

### Features:
- Automatically extracts key contract information from PDFs, such as Contract ID, Period of Performance, CLIN Descriptions, and Line Items.
- Error handling included to account for missing or incomplete data in PDFs.
- Outputs: Excel file (or CSV) with structured contract data for further analysis.


### Future Enhancements:
- Add support for batch PDF processing.
- Improve error handling and data validation.
- Extend output support to additional formats such as CSV or JSON.

## Example Usage

This tool extracts relevant contract information from all PDF files in the specified directory and outputs the results into an Excel file.

### Running the Program

1. Place all PDF files you want to scan in the `/PDF-Contract-Parser/` directory.
2. Run the Python script using the following command:

    ```bash
    python3 pdf_contract_parser.py
    ```

3. The output will be saved in an Excel file named `extracted_contract_data.xlsx` in the same directory.

### Example Output

Here is an example of the output generated by the script:

| Contract ID | POP           | Contract Value | CLIN Description | PO Number | Line Item | Line Item Value |
|-------------|---------------|----------------|------------------|-----------|-----------|----------------|
| None        | None          | None           | None             | None      | None      | None           |
| ...         | ...           | ...            | ...              | ...       | ...       | ...            |

The Excel file can be opened to view the extracted contract data in a structured format.

