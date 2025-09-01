import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime
import io
import base64
import os
from PIL import Image

# Configure Streamlit page
st.set_page_config(
    page_title="EPF Challan Data Extractor",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styling */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Header Styling */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    /* Card Styling */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(240, 147, 251, 0.3);
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .metric-card p {
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Upload Section */
    .upload-section {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        border: 2px dashed rgba(255, 255, 255, 0.5);
    }
    
    /* Process Button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    .stError {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    /* Table Styling */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Download Section */
    .download-section {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .download-section a {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        display: inline-block;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .download-section a:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        text-decoration: none;
        color: white;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 3rem;
        color: white;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 20px rgba(168, 237, 234, 0.3);
        transition: transform 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-3px);
    }
    
    .feature-card h4 {
        color: #667eea;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Status Indicators */
    .status-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-processing {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

def extract_summary_table(text):
    """
    Extract the Summary table (EPF, EPS, EDLI data)
    """
    summary_data = {
        'EPF_Subscribers': '',
        'EPS_Subscribers': '',
        'EDLI_Subscribers': '',
        'EPF_Total_Wages': '',
        'EPS_Total_Wages': '',
        'EDLI_Total_Wages': ''
    }
    
    try:
        # Extract subscriber counts - looking for the pattern after "Total Subscribers :"
        subscribers_pattern = r'Total Subscribers\s*:\s*(\d+)\s+(\d+)\s+(\d+)'
        subscribers_match = re.search(subscribers_pattern, text)
        if subscribers_match:
            summary_data['EPF_Subscribers'] = subscribers_match.group(1)
            summary_data['EPS_Subscribers'] = subscribers_match.group(2)
            summary_data['EDLI_Subscribers'] = subscribers_match.group(3)
        else:
            # Alternative pattern
            epf_sub_match = re.search(r'Total Subscribers\s*:\s*(\d+)', text)
            if epf_sub_match:
                summary_data['EPF_Subscribers'] = epf_sub_match.group(1)
            
            # Look for other subscriber numbers in the document
            numbers_after_epf = re.findall(r'(\d+)\s+(\d+)', text)
            if numbers_after_epf:
                summary_data['EPS_Subscribers'] = numbers_after_epf[0][1] if len(numbers_after_epf[0]) > 1 else ''
                if len(numbers_after_epf) > 1:
                    summary_data['EDLI_Subscribers'] = numbers_after_epf[1][1] if len(numbers_after_epf[1]) > 1 else ''
        
        # Extract wages - looking for the pattern after "Total Wages :"
        wages_pattern = r'Total Wages\s*:\s*([\d,]+)\s+([\d,]+)\s+([\d,]+)'
        wages_match = re.search(wages_pattern, text)
        if wages_match:
            summary_data['EPF_Total_Wages'] = wages_match.group(1).replace(',', '')
            summary_data['EPS_Total_Wages'] = wages_match.group(2).replace(',', '')
            summary_data['EDLI_Total_Wages'] = wages_match.group(3).replace(',', '')
        else:
            # Alternative extraction
            all_wages = re.findall(r'Total Wages\s*:\s*([\d,]+)', text)
            if all_wages:
                summary_data['EPF_Total_Wages'] = all_wages[0].replace(',', '')
                if len(all_wages) > 1:
                    summary_data['EPS_Total_Wages'] = all_wages[1].replace(',', '')
                if len(all_wages) > 2:
                    summary_data['EDLI_Total_Wages'] = all_wages[2].replace(',', '')
    
    except Exception as e:
        st.error(f"Error extracting summary table: {e}")
    
    return summary_data

def extract_contribution_table(text):
    """
    Extract the Contribution Details table with all A/C columns
    """
    contribution_data = {
        'Admin_Charges_AC01': '0',
        'Admin_Charges_AC02': '0',
        'Admin_Charges_AC10': '0',
        'Admin_Charges_AC21': '0',
        'Admin_Charges_AC22': '0',
        'Admin_Charges_Total': '0',
        'Employer_Share_AC01': '0',
        'Employer_Share_AC02': '0',
        'Employer_Share_AC10': '0',
        'Employer_Share_AC21': '0',
        'Employer_Share_AC22': '0',
        'Employer_Share_Total': '0',
        'Employee_Share_AC01': '0',
        'Employee_Share_AC02': '0',
        'Employee_Share_AC10': '0',
        'Employee_Share_AC21': '0',
        'Employee_Share_AC22': '0',
        'Employee_Share_Total': '0'
    }
    
    try:
        # Multiple patterns for Administration Charges row to handle different formats
        admin_patterns = [
            # Pattern 1: All values with commas possible
            r'Administration Charges\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)',
            # Pattern 2: Some values might be 0, others with commas
            r'Administration Charges\s+(\d+)\s+([\d,]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d,]+)',
            # Pattern 3: Flexible spacing and number format
            r'Administration Charges\s+(\d+)\s+(\d+,?\d*)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d,]+)',
            # Pattern 4: Very flexible with optional commas
            r'Administration Charges\s+(\d+)\s+([0-9,]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([0-9,]+)'
        ]
        
        admin_extracted = False
        for pattern in admin_patterns:
            admin_match = re.search(pattern, text)
            if admin_match:
                contribution_data['Admin_Charges_AC01'] = admin_match.group(1).replace(',', '')
                contribution_data['Admin_Charges_AC02'] = admin_match.group(2).replace(',', '')
                contribution_data['Admin_Charges_AC10'] = admin_match.group(3).replace(',', '')
                contribution_data['Admin_Charges_AC21'] = admin_match.group(4).replace(',', '')
                contribution_data['Admin_Charges_AC22'] = admin_match.group(5).replace(',', '')
                contribution_data['Admin_Charges_Total'] = admin_match.group(6).replace(',', '')
                admin_extracted = True
                break
        
        # If no pattern worked, try to extract at least the total
        if not admin_extracted:
            admin_total_patterns = [
                r'Administration Charges.*?(\d{2,}[\d,]*)',
                r'Administration Charges.*?(\d+,\d+)',
                r'Administration Charges.*?(\d{4,})'
            ]
            for pattern in admin_total_patterns:
                admin_match = re.search(pattern, text, re.MULTILINE)
                if admin_match:
                    contribution_data['Admin_Charges_Total'] = admin_match.group(1).replace(',', '')
                    break
        
        # Extract Employer's Share row with multiple patterns
        employer_patterns = [
            r'Employer\'?s Share Of\s+([\d,]+)\s+(\d+)\s+([\d,]+)\s+([\d,]+)\s+(\d+)\s+([\d,]+)',
            r'Employer\'?s Share Of\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)'
        ]
        
        employer_extracted = False
        for pattern in employer_patterns:
            employer_match = re.search(pattern, text)
            if employer_match:
                contribution_data['Employer_Share_AC01'] = employer_match.group(1).replace(',', '')
                contribution_data['Employer_Share_AC02'] = employer_match.group(2).replace(',', '')
                contribution_data['Employer_Share_AC10'] = employer_match.group(3).replace(',', '')
                contribution_data['Employer_Share_AC21'] = employer_match.group(4).replace(',', '')
                contribution_data['Employer_Share_AC22'] = employer_match.group(5).replace(',', '')
                contribution_data['Employer_Share_Total'] = employer_match.group(6).replace(',', '')
                employer_extracted = True
                break
        
        if not employer_extracted:
            employer_alt_pattern = r'Employer\'?s Share Of.*?([\d,]+)'
            employer_alt_match = re.search(employer_alt_pattern, text)
            if employer_alt_match:
                contribution_data['Employer_Share_Total'] = employer_alt_match.group(1).replace(',', '')
        
        # Extract Employee's Share row with multiple patterns
        employee_patterns = [
            r'Employee\'?s Share Of\s+([\d,]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d,]+)',
            r'Employee\'?s Share Of\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)'
        ]
        
        employee_extracted = False
        for pattern in employee_patterns:
            employee_match = re.search(pattern, text)
            if employee_match:
                contribution_data['Employee_Share_AC01'] = employee_match.group(1).replace(',', '')
                contribution_data['Employee_Share_AC02'] = employee_match.group(2).replace(',', '')
                contribution_data['Employee_Share_AC10'] = employee_match.group(3).replace(',', '')
                contribution_data['Employee_Share_AC21'] = employee_match.group(4).replace(',', '')
                contribution_data['Employee_Share_AC22'] = employee_match.group(5).replace(',', '')
                contribution_data['Employee_Share_Total'] = employee_match.group(6).replace(',', '')
                employee_extracted = True
                break
        
        if not employee_extracted:
            employee_alt_pattern = r'Employee\'?s Share Of.*?([\d,]+)'
            employee_alt_match = re.search(employee_alt_pattern, text)
            if employee_alt_match:
                contribution_data['Employee_Share_Total'] = employee_alt_match.group(1).replace(',', '')
    
    except Exception as e:
        st.error(f"Error extracting contribution table: {e}")
    
    return contribution_data

def extract_epf_data(pdf_file):
    """
    Extract EPF challan data from PDF file
    """
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        # Initialize data dictionary with ordered fields (grand_total_amount will be moved to end)
        data = {
            'Filename': pdf_file.name,
            'Establishment_code': '',
            'Establishment_name': '',
            'Wage_month': '',
            'Generation_date': '',
        }
        
        # Extract basic establishment details
        est_match = re.search(r'Establishment Code & Name\s+([A-Z0-9]+)\s+(.+?)(?=\s*Dues|\s*Address|\n)', text, re.DOTALL)
        if est_match:
            data['Establishment_code'] = est_match.group(1).strip()
            data['Establishment_name'] = est_match.group(2).strip()
        
        # Extract wage month - improved pattern to capture the full phrase
        month_patterns = [
            r'Dues for the wage month of\s*:?\s*(\w+\s+\d{4})',
            r'Dues for the wage month of\s+(\w+\s+\d{4})',
            r'wage month of\s*:?\s*(\w+\s+\d{4})'
        ]
        
        for pattern in month_patterns:
            month_match = re.search(pattern, text)
            if month_match:
                data['Wage_month'] = month_match.group(1).strip()
                break
        
        # Extract generation date
        gen_date_match = re.search(r'system generated challan on\s*(\d{2}-\w{3}-\d{4}\s+\d{2}:\d{2})', text)
        if gen_date_match:
            data['Generation_date'] = gen_date_match.group(1)
        
        # Extract Summary Table
        summary_data = extract_summary_table(text)
        data.update(summary_data)
        
        # Extract Contribution Details Table
        contribution_data = extract_contribution_table(text)
        data.update(contribution_data)
        
        # Extract grand total amount (this will be added at the end)
        grand_total_match = re.search(r'Grand Total\s*:\s*(.+?)\s*-?\s*([\d,]+)', text, re.DOTALL)
        if grand_total_match:
            data['Grand_total_amount'] = grand_total_match.group(2).replace(',', '')
        else:
            data['Grand_total_amount'] = ''
        
        return data, True, ""
        
    except Exception as e:
        return {}, False, str(e)

def create_summary_df(all_data):
    """
    Create a summary DataFrame from all extracted data with grand_total_amount as the last column
    """
    df = pd.DataFrame(all_data)
    
    # Reorder columns to put grand_total_amount at the end
    if 'Grand_total_amount' in df.columns:
        # Get all columns except grand_total_amount
        other_columns = [col for col in df.columns if col != 'Grand_total_amount']
        # Reorder with grand_total_amount at the end
        df = df[other_columns + ['Grand_total_amount']]
    
    return df

def display_detailed_tables(data):
    """
    Display the Summary and Contribution tables in proper format
    """
    st.markdown('<div class="section-header"><h3>📊 Summary Table</h3></div>', unsafe_allow_html=True)
    summary_df = pd.DataFrame({
        'Category': ['EPF', 'EPS', 'EDLI'],
        'Total Subscribers': [
            data.get('EPF_Subscribers', ''),
            data.get('EPS_Subscribers', ''),
            data.get('EDLI_Subscribers', '')
        ],
        'Total Wages (₹)': [
            f"{int(data.get('EPF_Total_Wages', '0')):,}" if data.get('EPF_Total_Wages', '').isdigit() else data.get('EPF_Total_Wages', ''),
            f"{int(data.get('EPS_Total_Wages', '0')):,}" if data.get('EPS_Total_Wages', '').isdigit() else data.get('EPS_Total_Wages', ''),
            f"{int(data.get('EDLI_Total_Wages', '0')):,}" if data.get('EDLI_Total_Wages', '').isdigit() else data.get('EDLI_Total_Wages', '')
        ]
    })
    st.dataframe(summary_df, use_container_width=True)
    
    st.markdown('<div class="section-header"><h3>💰 Contribution Details Table</h3></div>', unsafe_allow_html=True)
    contribution_df = pd.DataFrame({
        'Particulars': ['Administration Charges', 'Employer\'s Share', 'Employee\'s Share'],
        'A/C.01 (₹)': [
            f"{int(data.get('Admin_Charges_AC01', '0')):,}" if data.get('Admin_Charges_AC01', '').isdigit() else data.get('Admin_Charges_AC01', ''),
            f"{int(data.get('Employer_Share_AC01', '0')):,}" if data.get('Employer_Share_AC01', '').isdigit() else data.get('Employer_Share_AC01', ''),
            f"{int(data.get('Employee_Share_AC01', '0')):,}" if data.get('Employee_Share_AC01', '').isdigit() else data.get('Employee_Share_AC01', '')
        ],
        'A/C.02 (₹)': [
            f"{int(data.get('Admin_Charges_AC02', '0')):,}" if data.get('Admin_Charges_AC02', '').isdigit() else data.get('Admin_Charges_AC02', ''),
            f"{int(data.get('Employer_Share_AC02', '0')):,}" if data.get('Employer_Share_AC02', '').isdigit() else data.get('Employer_Share_AC02', ''),
            f"{int(data.get('Employee_Share_AC02', '0')):,}" if data.get('Employee_Share_AC02', '').isdigit() else data.get('Employee_Share_AC02', '')
        ],
        'A/C.10 (₹)': [
            f"{int(data.get('Admin_Charges_AC10', '0')):,}" if data.get('Admin_Charges_AC10', '').isdigit() else data.get('Admin_Charges_AC10', ''),
            f"{int(data.get('Employer_Share_AC10', '0')):,}" if data.get('Employer_Share_AC10', '').isdigit() else data.get('Employer_Share_AC10', ''),
            f"{int(data.get('Employee_Share_AC10', '0')):,}" if data.get('Employee_Share_AC10', '').isdigit() else data.get('Employee_Share_AC10', '')
        ],
        'A/C.21 (₹)': [
            f"{int(data.get('Admin_Charges_AC21', '0')):,}" if data.get('Admin_Charges_AC21', '').isdigit() else data.get('Admin_Charges_AC21', ''),
            f"{int(data.get('Employer_Share_AC21', '0')):,}" if data.get('Employer_Share_AC21', '').isdigit() else data.get('Employer_Share_AC21', ''),
            f"{int(data.get('Employee_Share_AC21', '0')):,}" if data.get('Employee_Share_AC21', '').isdigit() else data.get('Employee_Share_AC21', '')
        ],
        'A/C.22 (₹)': [
            f"{int(data.get('Admin_Charges_AC22', '0')):,}" if data.get('Admin_Charges_AC22', '').isdigit() else data.get('Admin_Charges_AC22', ''),
            f"{int(data.get('Employer_Share_AC22', '0')):,}" if data.get('Employer_Share_AC22', '').isdigit() else data.get('Employer_Share_AC22', ''),
            f"{int(data.get('Employee_Share_AC22', '0')):,}" if data.get('Employee_Share_AC22', '').isdigit() else data.get('Employee_Share_AC22', '')
        ],
        'TOTAL (₹)': [
            f"{int(data.get('Admin_Charges_Total', '0')):,}" if data.get('Admin_Charges_Total', '').isdigit() else data.get('Admin_Charges_Total', ''),
            f"{int(data.get('Employer_Share_Total', '0')):,}" if data.get('Employer_Share_Total', '').isdigit() else data.get('Employer_Share_Total', ''),
            f"{int(data.get('Employee_Share_Total', '0')):,}" if data.get('Employee_Share_Total', '').isdigit() else data.get('Employee_Share_Total', '')
        ]
    })
    st.dataframe(contribution_df, use_container_width=True)

def download_excel(df, filename="Epf_challan_data.xlsx"):
    """
    Create download link for Excel file
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='EPF_Challan_Data', index=False)
    
    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Download Excel Report</a>'
    return href

def main():
    # App header with PIL Image and columns approach
    try:
        logo = Image.open("kkc logo.png")
        
        st.markdown('<div class="custom-header">', unsafe_allow_html=True)

        # Create columns for logo and title
        col_logo, col_title = st.columns([3, 7])
        
        with col_logo:
            st.image(logo, width=700)  # Set to 700px width as requested
        
        with col_title:
            st.markdown("""
                <div style="padding-left: 2rem; display: flex; flex-direction: column; justify-content: center; height: 150px;">
                    <h1 style="color: black; font-family: 'Inter', sans-serif; font-weight: 700; font-size: 2.5rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                        EPF Challan Data Extractor
                    </h1>
                    <p style="color: rgba(255,255,255,0.9); font-family: 'Inter', sans-serif; font-size: 1.1rem; margin: 0.5rem 0 0 0; font-weight: 300;">
                        Professional • Efficient • Reliable Data Processing
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        # Fallback header if logo can't be loaded
        st.markdown("""
        <div class="custom-header">
            <h1 style="color: white; text-align: center; margin: 0; font-size: 2.5rem; font-weight: 700;">🏛️ EPF Challan Data Extractor</h1>
            <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 0.5rem 0 0 0;">Professional tool for extracting and analyzing EPF contribution data from multiple PDF files</p>
        </div>
        """, unsafe_allow_html=True)
        st.warning(f"Could not load logo: {e}")
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1rem;">
            <h2 style="margin: 0; text-align: center;">📋 How to Use</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>🔄 Step 1: Upload</h4>
            <p>Select one or more EPF challan PDF files from your computer</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>⚡ Step 2: Process</h4>
            <p>Click the process button to extract data automatically</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Step 3: Analyze</h4>
            <p>Review extracted data with structured tables and summaries</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>💾 Step 4: Export</h4>
            <p>Download results as Excel file for further analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1.5rem; border-radius: 12px; margin-top: 2rem;">
            <h3 style="color: #667eea; margin-top: 0;">🎯 Key Features</h3>
            <ul style="color: #333; padding-left: 1rem;">
                <li>✅ Batch PDF processing</li>
                <li>🔍 Smart data extraction</li>
                <li>📈 Interactive dashboards</li>
                <li>📋 Detailed contribution tables</li>
                <li>💼 Professional Excel reports</li>
                <li>🚀 Lightning-fast processing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # File upload section with professional styling
    st.markdown("""
    <div class="upload-section">
        <h2 style="color: #667eea; margin-bottom: 1rem;">📁 Upload EPF Challan Files</h2>
        <p style="color: #666; margin-bottom: 1.5rem;">Drag and drop or click to select your PDF files</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "",
        type="pdf",
        accept_multiple_files=True,
        help="Select one or more EPF challan PDF files for processing",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        # Success message with file count
        st.markdown(f"""
        <div class="status-success">
            ✅ {len(uploaded_files)} file(s) uploaded successfully and ready for processing!
        </div>
        """, unsafe_allow_html=True)
        
        # Display uploaded files in a nice format
        st.markdown('<div class="section-header"><h3>📄 Uploaded Files</h3></div>', unsafe_allow_html=True)
        
        cols = st.columns(min(len(uploaded_files), 4))
        for i, uploaded_file in enumerate(uploaded_files):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="info-card" style="text-align: center;">
                    <h4 style="color: #667eea; margin-bottom: 0.5rem;">📄</h4>
                    <p style="font-size: 0.9rem; margin: 0;">{uploaded_file.name}</p>
                    <small style="color: #666;">{uploaded_file.size} bytes</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Process files button with enhanced styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            process_clicked = st.button("🚀 Process All Files", type="primary", use_container_width=True)
        
        if process_clicked:
            all_data = []
            errors = []
            
            # Enhanced progress section
            st.markdown("""
            <div class="status-processing">
                🔄 Processing files... Please wait
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.markdown(f"""
                <div style="text-align: center; padding: 1rem;">
                    <h4 style="color: #667eea;">Processing: {uploaded_file.name}</h4>
                    <p style="color: #666;">File {i+1} of {len(uploaded_files)}</p>
                </div>
                """, unsafe_allow_html=True)
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Extract data from PDF
                data, success, error = extract_epf_data(uploaded_file)
                
                if success:
                    all_data.append(data)
                else:
                    errors.append(f"{uploaded_file.name}: {error}")
            
            status_text.markdown("""
            <div class="status-success" style="text-align: center; margin: 1rem 0;">
                ✅ Processing completed successfully!
            </div>
            """, unsafe_allow_html=True)
            
            # Display results
            if all_data:
                st.markdown(f"""
                <div class="status-success" style="text-align: center; margin: 2rem 0;">
                    🎉 Successfully processed {len(all_data)} files!
                </div>
                """, unsafe_allow_html=True)
                
                # Create DataFrame
                df = create_summary_df(all_data)
                
                # Enhanced metrics display
                st.markdown('<div class="section-header"><h3>📊 Quick Analytics</h3></div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{len(all_data)}</h3>
                        <p>Files Processed</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    total_amount = df['Grand_total_amount'].apply(lambda x: int(x) if x and str(x).isdigit() else 0).sum()
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>₹{total_amount:,}</h3>
                        <p>Total Amount</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    total_epf_subscribers = df['EPF_Subscribers'].apply(lambda x: int(x) if x and str(x).isdigit() else 0).sum()
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{total_epf_subscribers:,}</h3>
                        <p>EPF Subscribers</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    unique_establishments = df['Establishment_name'].nunique()
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{unique_establishments}</h3>
                        <p>Unique Establishments</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display consolidated data table
                st.markdown('<div class="section-header"><h3>📋 Complete Extracted Data</h3></div>', unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True, height=400)
                
                # Enhanced download section
                st.markdown("""
                <div class="download-section">
                    <h3 style="color: #667eea; margin-bottom: 1rem;">💾 Export Your Data</h3>
                    <p style="color: #666; margin-bottom: 1.5rem;">Download your processed EPF data as a professional Excel report</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    excel_link = download_excel(df, f"EPF_Challan_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
                    st.markdown(f'<div class="download-section">{excel_link}</div>', unsafe_allow_html=True)
                
                # Individual file details with enhanced styling
                st.markdown('<div class="section-header"><h3>📄 Detailed File Analysis</h3></div>', unsafe_allow_html=True)
                
                for i, data in enumerate(all_data):
                    with st.expander(f"📄 File {i+1}: {data['Filename']}", expanded=False):
                        
                        # Enhanced establishment info display
                        st.markdown("""
                        <div class="info-card">
                            <h4 style="color: #667eea; margin-bottom: 1rem;">🏢 Establishment Information</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div class="info-card">
                                <p><strong>Code:</strong> {data['Establishment_code']}</p>
                                <p><strong>Name:</strong> {data['Establishment_name']}</p>
                                <p><strong>Wage Month:</strong> {data['Wage_month']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="info-card">
                                <p><strong>Generation Date:</strong> {data['Generation_date']}</p>
                                <p><strong>Grand Total:</strong> ₹{int(data['Grand_total_amount']):,}" if data['Grand_total_amount'].isdigit() else f"₹{data['Grand_total_amount']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Display the structured tables
                        display_detailed_tables(data)
                
                # Debug section with professional styling
                with st.expander("🔧 Advanced: Raw Data Inspector", expanded=False):
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <h4 style="color: #667eea; margin: 0;">🔍 Raw Extracted Values</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #666;">View the unprocessed data extracted from each PDF file</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, data in enumerate(all_data):
                        st.markdown(f"<h4 style='color: #667eea;'>File {i+1}: {data['Filename']}</h4>", unsafe_allow_html=True)
                        
                        debug_cols = st.columns(3)
                        
                        with debug_cols[0]:
                            st.markdown("""
                            <div class="info-card">
                                <h5 style="color: #f093fb;">Admin Charges (Raw)</h5>
                                <p><strong>AC01:</strong> {}</p>
                                <p><strong>AC02:</strong> {}</p>
                                <p><strong>AC10:</strong> {}</p>
                                <p><strong>AC21:</strong> {}</p>
                                <p><strong>AC22:</strong> {}</p>
                                <p><strong>Total:</strong> {}</p>
                            </div>
                            """.format(
                                data.get('Admin_Charges_AC01', 'Not found'),
                                data.get('Admin_Charges_AC02', 'Not found'),
                                data.get('Admin_Charges_AC10', 'Not found'),
                                data.get('Admin_Charges_AC21', 'Not found'),
                                data.get('Admin_Charges_AC22', 'Not found'),
                                data.get('Admin_Charges_Total', 'Not found')
                            ), unsafe_allow_html=True)
                        
                        with debug_cols[1]:
                            st.markdown("""
                            <div class="info-card">
                                <h5 style="color: #f093fb;">Employer Share (Raw)</h5>
                                <p><strong>AC01:</strong> {}</p>
                                <p><strong>AC02:</strong> {}</p>
                                <p><strong>AC10:</strong> {}</p>
                                <p><strong>AC21:</strong> {}</p>
                                <p><strong>AC22:</strong> {}</p>
                                <p><strong>Total:</strong> {}</p>
                            </div>
                            """.format(
                                data.get('Employer_Share_AC01', 'Not found'),
                                data.get('Employer_Share_AC02', 'Not found'),
                                data.get('Employer_Share_AC10', 'Not found'),
                                data.get('Employer_Share_AC21', 'Not found'),
                                data.get('Employer_Share_AC22', 'Not found'),
                                data.get('Employer_Share_Total', 'Not found')
                            ), unsafe_allow_html=True)
                        
                        with debug_cols[2]:
                            st.markdown("""
                            <div class="info-card">
                                <h5 style="color: #f093fb;">Employee Share (Raw)</h5>
                                <p><strong>AC01:</strong> {}</p>
                                <p><strong>AC02:</strong> {}</p>
                                <p><strong>AC10:</strong> {}</p>
                                <p><strong>AC21:</strong> {}</p>
                                <p><strong>AC22:</strong> {}</p>
                                <p><strong>Total:</strong> {}</p>
                            </div>
                            """.format(
                                data.get('Employee_Share_AC01', 'Not found'),
                                data.get('Employee_Share_AC02', 'Not found'),
                                data.get('Employee_Share_AC10', 'Not found'),
                                data.get('Employee_Share_AC21', 'Not found'),
                                data.get('Employee_Share_AC22', 'Not found'),
                                data.get('Employee_Share_Total', 'Not found')
                            ), unsafe_allow_html=True)
                        
                        if i < len(all_data) - 1:
                            st.markdown("<hr style='border: 1px solid #eee; margin: 2rem 0;'>", unsafe_allow_html=True)
            
            # Display errors if any
            if errors:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 12px; color: white; margin: 2rem 0;">
                    <h3>⚠️ Processing Errors</h3>
                    <p>Some files could not be processed:</p>
                </div>
                """, unsafe_allow_html=True)
                
                for error in errors:
                    st.markdown(f"""
                    <div class="info-card" style="border-left: 4px solid #fa709a;">
                        <p style="color: #fa709a; margin: 0;">❌ {error}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        # Welcome message when no files uploaded
        st.markdown("""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 3rem; border-radius: 15px; text-align: center; margin: 2rem 0;">
            <h2 style="color: #667eea; margin-bottom: 1rem;">👋 Welcome to EPF Challan Extractor</h2>
            <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">Upload your EPF challan PDF files to get started with automated data extraction and analysis</p>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h4 style="color: #667eea; margin: 0;">⚡ Fast Processing</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">Lightning-fast PDF extraction</p>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h4 style="color: #667eea; margin: 0;">📊 Smart Analysis</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">Intelligent data structuring</p>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h4 style="color: #667eea; margin: 0;">💼 Professional Reports</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">Excel-ready output format</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Professional footer
    st.markdown("""
    <div class="footer">
        <h3 style="margin-bottom: 1rem;">🏛️ EPF Challan Data Extractor</h3>
        <p style="margin: 0; opacity: 0.9;">Designed for Finance Professionals</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.7;">© 2025 - Streamline your EPF data processing workflow</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
