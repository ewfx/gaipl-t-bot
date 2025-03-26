import streamlit as st
from openai import OpenAI
import os
from prompt import SYSTEM_PROMPT
from config import load_config_data

chat_model_1 = load_config_data["GROQ_llama_3_3_70B_SPECTEC"]
chat_model_2 = load_config_data["GROQ_llama_3_3_70B_VERSATILE"]
api_key = load_config_data["GROQ_API_KEY"]
base_url = load_config_data["GROQ_BASE_URL"]

# Set up the page
st.set_page_config(page_title="Indian Tax Regime Assistant", page_icon="🇮🇳")
st.title("Indian Tax Regime Calculator & Assistant")

client = OpenAI(api_key=api_key,base_url=base_url)

# Tax regime information (as of 2023-24)
NEW_REGIME_TAX_SLABS = [
    (0, 3_00_000, 0),
    (3_00_001, 6_00_000, 5),
    (6_00_001, 9_00_000, 10),
    (9_00_001, 12_00_000, 15),
    (12_00_001, 15_00_000, 20),
    (15_00_001, float('inf'), 25)
]

STANDARD_DEDUCTION = 50_000  # Standard deduction under new regime

def calculate_new_regime_tax(income):
    tax = 0
    remaining_income = income
    
    # Apply standard deduction
    taxable_income = max(income - STANDARD_DEDUCTION, 0)
    remaining_income = taxable_income
    
    for slab in NEW_REGIME_TAX_SLABS:
        min_slab, max_slab, percent = slab
        if remaining_income <= 0:
            break
        
        slab_amount = min(max_slab, remaining_income) - min_slab
        if slab_amount > 0:
            tax += (slab_amount * percent) / 100
            remaining_income -= slab_amount
    
    # Add health and education cess (4%)
    total_tax = tax * 1.04
    
    return round(total_tax)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm your Indian tax assistant. How can I help you with the new tax regime today?"})

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask about India's new tax regime..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check if user is asking for tax calculation
    if any(word in prompt.lower() for word in ["calculate", "how much tax", "liability", "income of"]):
        try:
            # Extract income amount from prompt
            income = None
            words = prompt.split()
            for i, word in enumerate(words):
                if word.isdigit():
                    income = int(word)
                    if i > 0 and words[i-1] in ["lakh", "lakhs"]:
                        income *= 100000
                    break
            
            if income:
                tax = calculate_new_regime_tax(income)
                response = f"For an annual income of ₹{income:,} under the new regime:\n\n"
                response += f"- Standard deduction: ₹{STANDARD_DEDUCTION:,}\n"
                response += f"- Taxable income: ₹{max(income - STANDARD_DEDUCTION, 0):,}\n"
                response += f"- Estimated tax liability: ₹{tax:,} (including 4% cess)\n\n"
                response += "Note: This is an estimate. Actual tax may vary based on specific deductions and surcharges."
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(response)
            else:
                raise ValueError("Income not specified")
        
        except Exception as e:
            response = "I couldn't calculate the tax. Please provide your income clearly, like 'Calculate tax for 8 lakhs'."
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
    else:
        # Use OpenAI API for general queries
        # try:
            response = client.chat.completions.create(
                model=chat_model_2,
                messages=st.session_state.messages,
                temperature=0.3
            )
            ai_response = response.choices[0].message.content
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(ai_response)
        
        # except Exception as e:
        #     st.error("Sorry, I'm having trouble responding. Please try again later.")

# Sidebar with tax information
with st.sidebar:
    st.header("New Tax Regime (2023-24)")
    st.subheader("Tax Slabs (Individuals <60 years)")
    
    for slab in NEW_REGIME_TAX_SLABS:
        min_slab, max_slab, percent = slab
        if max_slab == float('inf'):
            st.write(f"Above ₹{min_slab:,}: {percent}%")
        else:
            st.write(f"₹{min_slab:,} - ₹{max_slab:,}: {percent}%")
    
    st.write("\nStandard deduction: ₹50,000")
    st.write("Health & Education Cess: 4% of tax")
    
    st.markdown("---")
    st.caption("Note: This is for informational purposes only. Consult a CA for specific advice.")
