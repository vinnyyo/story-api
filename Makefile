run:
	uvicorn story-api:app --reload

runout:
	uvicorn story-api:app --host 0.0.0.0 --port 8000

surunout:
	uvicorn story-api:app --host 0.0.0.0 --port 8000