# DETIKNews-API
DETIK.com web API build using Python FastAPI

## Install Depedencies
If you're using pipenv
```bash
pipenv install
```

If not use any environment:
```bash
python -m pip install httpx selectolax fastapi uvicorn
```

## Run
```bash
uvicorn app:app --reload
```

## Test
[http://127.0.0.1:8000/scrape/?keyword=teknologi&pages=10](http://127.0.0.1:8000/scrape/?keyword=teknologi&pages=10)

[EDIT the **keyword** and **pages** value]
