# AI Generated Dungeons and Dragons Experience 

An OpenAI generated dungeons and dragons experience. Imagine reading a page from a story book, saying what you want the hero to do and seeing what happens to the hero in the story on the next page. Well now you don't need to imagine it because it's here. Just clone the repo, paste your OpenAI API token into `story-api.py` and run these commands:

```{bash}
pip install -r requirements.txt
uvicorn story-api:app --reload
```

Then open `http://127.0.0.1:8000/` in the browser of your choice and immerse yourself in the experience.