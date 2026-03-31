(See project README)

# HealthBot_Streamlit

A small Streamlit prototype for patient education. Uses Cohere for LLM generation and Tavily for search.

Setup:

1. Create `config.env` with your keys:

```
COHERE_API_KEY="your-cohere-key"
TAVILY_API_KEY="tvly-..."
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

Notes:

- The code uses a lightweight Cohere adapter in `healthbot_graph.py` that
	provides an `invoke(prompt)` interface similar to the previous OpenAI
	wrapper. Adjust the Cohere model and generation parameters there if needed.
