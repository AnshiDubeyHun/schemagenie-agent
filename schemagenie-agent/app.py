import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="SchemaGenie | Powered by Groq", 
    page_icon="⚡", 
    layout="wide"
)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ Missing GROQ_API_KEY. Please check your .env file.")
    st.stop()

client = Groq(api_key=api_key.strip())
MODEL_NAME = "openai/gpt-oss-120b"

st.title("⚡ SchemaGenie: AI SQL Architect & Optimizer")
st.caption("Powered by Groq High-Speed Inference Engine (100% Free Tier)")

with st.sidebar:
    st.header("Settings")
    st.markdown("**Engine:** `Groq LPU`")
    st.markdown(f"**Model:** `{MODEL_NAME}`")
    dialect = st.selectbox("Database Engine", ["PostgreSQL", "MySQL", "SQLite", "Snowflake"])
    mode = st.radio(
        "Mode",
        ["Text-to-SQL Generator", "SQL Query Optimizer"]
    )

if mode == "Text-to-SQL Generator":
    col1, col2 = st.columns(2)
    with col1:
        schema_ddl = st.text_area(
            "Schema / Table Definitions (Optional)",
            placeholder="CREATE TABLE employees (\n  emp_id INT PRIMARY KEY,\n  dept_id INT,\n  salary NUMERIC\n);",
            height=200
        )
    with col2:
        user_query = st.text_area(
            "What data do you want to retrieve?",
            placeholder="Show the top 3 highest-earning employees in each department with average dept salary.",
            height=200
        )

    if st.button("Generate SQL", type="primary"):
        if not user_query.strip():
            st.warning("Please describe what data you want to query.")
        else:
            schema_context = schema_ddl.strip() if schema_ddl.strip() else "Infer standard logical tables as needed."
            prompt = (
                f"You are a principal database architect.\n"
                f"Target Dialect: {dialect}\n"
                f"Schema context:\n{schema_context}\n\n"
                f"User Question: \"{user_query}\"\n\n"
                f"Instructions:\n"
                f"1. Provide the optimized SQL query inside a markdown ```sql code block.\n"
                f"2. Explain the query logic in 2-3 clear bullet points.\n"
                f"3. Suggest indexing recommendations for best performance."
            )
            with st.spinner("Groq is generating SQL at high speed..."):
                try:
                    res = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2,
                    )
                    st.markdown("### Generated Query")
                    st.markdown(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Inference error: {e}")

else:
    sql_input = st.text_area(
        "Paste Existing SQL Query to Analyze",
        placeholder="SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE total > 100);",
        height=200
    )

    if st.button("Analyze & Optimize", type="primary"):
        if not sql_input.strip():
            st.warning("Please provide a SQL query to audit.")
        else:
            prompt = (
                f"You are a database performance tuner.\n"
                f"Target Dialect: {dialect}\n"
                f"Query to optimize:\n"
                f"```sql\n{sql_input}\n```\n\n"
                f"Instructions:\n"
                f"1. Identify performance bottlenecks (anti-patterns, full table scans, subquery traps).\n"
                f"2. Rewrite the query for optimal execution speed inside a ```sql code block.\n"
                f"3. Provide concrete CREATE INDEX statements to support it."
            )
            with st.spinner("Analyzing query execution bottlenecks..."):
                try:
                    res = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                    )
                    st.markdown("### Optimization Audit")
                    st.markdown(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Inference error: {e}")