import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import fitz
import io
import re
import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# ------------------------------
# BASIC ACCESS CONTROL
# ------------------------------

PASSWORD = "intellicredit"

password = st.sidebar.text_input("Enter Access Password", type="password")

if password != PASSWORD:
    st.warning("Unauthorized access. Please enter valid password.")
    st.stop()


# ------------------------------
# SECURITY CONSTANTS
# ------------------------------

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


# ------------------------------
# INPUT SANITIZATION
# ------------------------------

def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9\s]", "", text)


# ------------------------------
# CAM PDF GENERATOR
# ------------------------------

def generate_cam_pdf(company, sector, promoter, revenue, debt, score, loan_amount, decision):

    buffer = io.BytesIO()
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Credit Appraisal Memo", styles['Title']))
    elements.append(Spacer(1,20))

    elements.append(Paragraph(f"Company: {company}", styles['Normal']))
    elements.append(Paragraph(f"Sector: {sector}", styles['Normal']))
    elements.append(Paragraph(f"Promoter: {promoter}", styles['Normal']))
    elements.append(Spacer(1,10))

    elements.append(Paragraph(f"Revenue: ₹{revenue} Cr", styles['Normal']))
    elements.append(Paragraph(f"Debt: ₹{debt} Cr", styles['Normal']))
    elements.append(Paragraph(f"Credit Score: {score}", styles['Normal']))
    elements.append(Spacer(1,10))

    elements.append(Paragraph(f"Loan Recommendation: ₹{loan_amount} Cr", styles['Normal']))
    elements.append(Paragraph(f"Final Lending Decision: {decision}", styles['Normal']))

    doc = SimpleDocTemplate(buffer)
    doc.build(elements)

    buffer.seek(0)

    return buffer


# ------------------------------
# UI START
# ------------------------------

st.title("IntelliCredit AI")
st.subheader("AI-Powered Corporate Credit Decision Engine")

st.sidebar.write("Session started:", datetime.datetime.now())


# ------------------------------
# COMPANY INFORMATION
# ------------------------------

st.header("Company Information")

company = clean_text(st.text_input("Company Name"))
sector = clean_text(st.text_input("Sector"))
promoter = clean_text(st.text_input("Promoter Name"))


# ------------------------------
# FINANCIAL DATASET
# ------------------------------

st.header("Upload Financial Dataset")

uploaded_file = st.file_uploader("Upload Financial CSV", type=["csv"])

if uploaded_file is not None:

    if uploaded_file.size > MAX_FILE_SIZE:
        st.error("File too large. Maximum size allowed is 5MB.")
        st.stop()

    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        st.error("Invalid or corrupted CSV file.")
        st.stop()

    required_columns = ["revenue_cr", "total_debt_cr"]

    if not all(col in df.columns for col in required_columns):
        st.error("Dataset must contain 'revenue_cr' and 'total_debt_cr' columns.")
        st.stop()

    st.subheader("Financial Data (Preview)")
    st.dataframe(df.head())

    revenue = df["revenue_cr"].iloc[-1]
    debt = df["total_debt_cr"].iloc[-1]


    # ------------------------------
    # CREDIT SCORE
    # ------------------------------

    score = 72 if revenue > 20 else 55

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Credit Score"},
        gauge={
            'axis': {'range': [0,100]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0,50], 'color': "red"},
                {'range': [50,70], 'color': "orange"},
                {'range': [70,100], 'color': "lightgreen"}
            ]
        }
    ))

    st.plotly_chart(gauge)


    # ------------------------------
    # RISK INDICATORS
    # ------------------------------

    st.subheader("Risk Indicators")

    if debt > revenue:
        st.warning("High debt compared to revenue")

    if revenue > 20:
        st.success("Strong revenue growth detected")

    if score < 60:
        st.error("Credit risk is high")
    else:
        st.info("Moderate credit risk")


    # ------------------------------
    # FIVE C'S RADAR CHART
    # ------------------------------

    categories = ['Character','Capacity','Capital','Collateral','Conditions']
    values = [14,18,16,10,13]

    radar = go.Figure()

    radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself'
    ))

    radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=False
    )

    st.plotly_chart(radar)


    # ------------------------------
    # LOAN RECOMMENDATION
    # ------------------------------

    st.subheader("Loan Recommendation")

    loan_amount = revenue * 0.5
    interest_rate = 11.2

    st.write(f"Recommended Loan Limit: ₹{loan_amount} Cr")
    st.write(f"Suggested Interest Rate: {interest_rate}%")


    # ------------------------------
    # AI DECISION EXPLANATION
    # ------------------------------

    st.subheader("AI Decision Explanation")

    if debt > revenue:
        st.write("• Debt is higher than revenue which increases financial risk.")

    if revenue > 20:
        st.write("• Revenue growth is strong improving repayment capacity.")

    if score >= 70:
        st.write("• Overall credit profile appears stable.")
    else:
        st.write("• Credit profile indicates elevated lending risk.")


    # ------------------------------
    # FINAL LENDING DECISION
    # ------------------------------

    st.subheader("Final Lending Decision")

    if score >= 75:
        decision = "Approve"
    elif score >= 60:
        decision = "Approve with Conditions"
    else:
        decision = "Reject"

    st.write("Decision:", decision)


    # ------------------------------
    # CREDIT MEMO
    # ------------------------------

    if st.button("Generate Credit Appraisal Memo"):

        st.subheader("Credit Appraisal Memo")

        st.write("Company:", company)
        st.write("Sector:", sector)
        st.write("Promoter:", promoter)

        st.write("Revenue:", revenue)
        st.write("Debt:", debt)

        st.write("Credit Score:", score)
        st.write("Loan Recommendation:", loan_amount, "Cr")
        st.write("Final Decision:", decision)

        pdf = generate_cam_pdf(company, sector, promoter, revenue, debt, score, loan_amount, decision)

        st.download_button(
            label="Download CAM Report (PDF)",
            data=pdf,
            file_name="credit_appraisal_memo.pdf",
            mime="application/pdf"
        )


# ------------------------------
# ANNUAL REPORT ANALYSIS
# ------------------------------

st.header("Upload Annual Report")

pdf_file = st.file_uploader("Upload Annual Report PDF", type=["pdf"])

if pdf_file:

    if pdf_file.size > MAX_FILE_SIZE:
        st.error("PDF file too large. Max 5MB allowed.")
        st.stop()

    try:
        pdf = fitz.open(stream=pdf_file.read(), filetype="pdf")
    except Exception:
        st.error("Invalid or corrupted PDF file.")
        st.stop()

    text = ""

    for page in pdf[:10]:  # limit parsing
        text += page.get_text()

    st.subheader("Extracted Text Preview")
    st.write(text[:1000])

    st.subheader("AI Risk Insights")

    risk_words = ["litigation","default","loss","debt"]

    found = []

    for word in risk_words:
        if word in text.lower():
            found.append(word)

    if found:
        st.warning(f"Risk indicators found: {', '.join(found)}")
    else:
        st.success("No major risk keywords detected.")