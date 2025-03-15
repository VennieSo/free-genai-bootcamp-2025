# Kana Learning App

This is Darya Petrashka's Kana Learning App from https://github.com/dashapetr/kana--streamlit-app. We updated the model download location to run on our environment, and integrated it with our Lang Portal.

Since this app is for our absolute beginner students, we will leave it as-is for kana studying.


## Instructions

### Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download OCR model

```sh
python3 preload_model.py
```

### Run

```sh
streamlit run init_streamlit_app.py
```
