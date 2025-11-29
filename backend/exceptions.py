from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback

def add_exception_handlers(app: FastAPI):

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        print("Uncaught exception:", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal server error occurred."}
        )
