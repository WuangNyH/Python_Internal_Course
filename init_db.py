# from contextlib import asynccontextmanager
#
# from fastapi import FastAPI
#
# from configs.database import engine, Base
# import models # đảm bảo models được import để Base.metadata có tables
#
#
# @asynccontextmanager
# async def db_lifespan(app: FastAPI):
#     Base.metadata.create_all(bind=engine)
#     yield
#     print("App shutting down...")
#     engine.dispose()