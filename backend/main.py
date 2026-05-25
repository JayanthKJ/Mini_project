from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def message():
    return "Exploring Adversity Quotient of Adoloscents Behavioural Impact."