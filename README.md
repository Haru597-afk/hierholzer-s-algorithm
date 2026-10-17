# Hierholzer Algorithm Lab — Streamlit (fresh rebuild)

This is a fresh Streamlit project. The entry file is **`streamlit_app.py`** (not `app.py`) specifically to avoid accidentally launching an old Flask `app.py` from the existing repository.

## Deploy on Streamlit Community Cloud
1. Download and extract this ZIP.
2. Upload `streamlit_app.py`, `requirements.txt`, and `README.md` to the **root** of your GitHub repository and commit them to the branch you deploy.
3. In Streamlit Community Cloud, open the app's **Settings** and set **Main file path** to exactly `streamlit_app.py`.
4. Save the settings and reboot/redeploy the app.
5. If the app is already attached to a different repository or branch, select the repository and branch where you committed these files.

## Why this version changes the entry filename
The previous error traceback showed Streamlit Cloud executing `app.py` line 53 with `app.run(host="127.0.0.1", port=5000, debug=True)`, which is a Flask entry point. This project deliberately uses `streamlit_app.py`; changing the Main file path is required. Merely uploading the new file while leaving Main file path as `app.py` will keep launching the old code.

## Run locally
```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Features: graph editing, repeated undirected edges, degree/parity validation, Euler path/circuit detection, Hierholzer steps, and graph visualization. Self-loops are not supported. No Flask, `app.run()`, game mechanics, or persistent database.
