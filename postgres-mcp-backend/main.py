"""A simple FastAPI application that returns a greeting message."""
import os

from fastapi import FastAPI, Request
import logging
from dotenv import load_dotenv

import config
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


@app.get("/download-report")
async def download_report(request: Request):
    """Endpoint to download the report file."""
    import os
    from fastapi.responses import FileResponse
    file_path = request.query_params.get("file_path", None)
    return FileResponse(
        file_path,
        filename=os.path.basename(file_path)
    )


if __name__ == "__main__":
    import uvicorn
    port = int(config.PORT)
    uvicorn.run(app, host="0.0.0.0", port=port)
