from server import app

if __name__ == "__main__":
    print("Calling from main.py..........................")
    import uvicorn
    uvicorn.run(app)