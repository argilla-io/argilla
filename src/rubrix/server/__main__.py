if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "rubrix.server.server:app",
        port=6900,
        host="0.0.0.0",
        reload=True,
        access_log=True,
    )
