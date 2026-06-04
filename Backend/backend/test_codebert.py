import asyncio
from app.ml.factory import get_ml_model

async def main():
    print("Loading ML model...")
    model = get_ml_model()
    print("Model loaded:", model.__class__.__name__)
    
    code = "import os\nos.system('rm -rf /')"
    print(f"Testing vulnerable code: {code!r}")
    prediction = model.predict(code)
    print("Prediction:", prediction.to_dict())
    
    safe_code = "print('Hello world')"
    print(f"Testing safe code: {safe_code!r}")
    prediction_safe = model.predict(safe_code)
    print("Prediction:", prediction_safe.to_dict())

if __name__ == "__main__":
    asyncio.run(main())
