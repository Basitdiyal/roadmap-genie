import streamlit as st
import requests
from fpdf import FPDF
import io

# ------------------------------
# CONFIG
# ------------------------------
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/roadmap"  # Replace with your n8n webhook URL

# ------------------------------
# STREAMLIT UI
# ------------------------------
st.set_page_config(page_title="Roadmap Genie", page_icon="🧭", layout="wide")

st.title("🧭 AI Roadmap Genie")
st.markdown("Get a **personalized roadmap** for your career interest, built by an AI Industry Expert Agent.")

# Input Fields
interest = st.text_input("💡 What skill or field are you interested in?", placeholder="e.g. Data Science, Web Development, Cybersecurity")
level = st.selectbox("🎯 Select your current level:", ["Beginner", "Intermediate", "Advanced"])

if st.button("🚀 Generate Roadmap"):
    if not interest:
        st.warning("Please enter your interest first.")
    else:
        with st.spinner("🔎 AI is crafting your roadmap..."):
            try:
                # Send data to n8n webhook
                response = requests.post(N8N_WEBHOOK_URL, json={"interest": interest, "level": level})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # If webhook returns a list, take the first item
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]

                    # ------------------------------
                    # SHOW ROADMAP
                    # ------------------------------
                    st.subheader("📘 Your Personalized Roadmap")
                    st.markdown(data.get("roadmap", "No roadmap returned."))

                    # ------------------------------
                    # SHOW RESOURCES
                    # ------------------------------
                    st.subheader("📚 Recommended Resources")
                    st.write("**Free Resources:**")
                    for res in data.get("resources", {}).get("free", []):
                        st.markdown(f"- {res}")

                    st.write("**Paid Resources:**")
                    for res in data.get("resources", {}).get("paid", []):
                        st.markdown(f"- {res}")

                    # ------------------------------
                    # SHOW CAREER PATHS
                    # ------------------------------
                    st.subheader("💼 Career Path Suggestions")
                    careers = data.get("careers", [])
                    if careers:
                        for career in careers:
                            st.write(f"- {career}")
                    else:
                        st.write("No career suggestions available.")

                    # ------------------------------
                    # CREATE PDF
                    # ------------------------------
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.multi_cell(0, 10, f"Roadmap for {interest} ({level})\n\n")
                    pdf.multi_cell(0, 10, "Roadmap:\n" + data.get("roadmap", ""))
                    pdf.multi_cell(0, 10, "\nFree Resources:\n" + "\n".join(data.get("resources", {}).get("free", [])))
                    pdf.multi_cell(0, 10, "\nPaid Resources:\n" + "\n".join(data.get("resources", {}).get("paid", [])))
                    pdf.multi_cell(0, 10, "\nCareer Suggestions:\n" + "\n".join(careers))

                    # Generate PDF as bytes
                    pdf_bytes = pdf.output(dest='S').encode('latin1')

                    # Provide download button
                    st.download_button(
                        label="📥 Download Roadmap as PDF",
                        data=pdf_bytes,
                        file_name="roadmap.pdf",
                        mime="application/pdf"
                    )

                else:
                    st.error(f"Error from backend: {response.text}")

            except Exception as e:
                st.error(f"Error: {e}")

