from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn
from db.check_server import check_mongo_server
from routers.etl import router as etl_router
from routers.etl_artifacts import router as etl_artifacts_router
from routers.stock_artifacts import router as stock_artifacts_router
from routers.performance_compare import router as performance_router
from routers.top_stocks import router as top_stocks_router


app = FastAPI(
    title="Stock ETL API",
    description="API for managing the Stock ETL process.",
    version="1.0.0"
)

@app.get("/", include_in_schema=False)
async def root_redirect():
    """
    Redirects the root URL to the /docs page.
    """
    return RedirectResponse(url="/docs")

@app.get("/root")
async def root():
    return {"message": "Hello, welcome to the Stock ETL API!"}


@app.get("/check_mongo_sever", tags=["Mongo"])
async def check_mongo_sever():
    if check_mongo_server():
        return {"message": "Mongo server is up and running"}
    return {"message": "Mongo server is NOT running"}


# Include the router from the routers folder
app.include_router(etl_router, prefix="/api", tags=["ETL"])
app.include_router(etl_artifacts_router, prefix="/api", tags=["Mongo"])
app.include_router(stock_artifacts_router, prefix="/api", tags=["Mongo"])
app.include_router(top_stocks_router, prefix="/api", tags=["Reports"])
app.include_router(performance_router, prefix="/api", tags=["Reports"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
