"""A simple FastAPI application that returns a greeting message."""
import uvicorn
from fastapi import FastAPI
import logging
from dotenv import load_dotenv

from agents import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

logging.getLogger("strands").setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()],
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat", tags=["chat"], include_in_schema=False)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8018)

