from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel

router = APIRouter()


class RandomInput(BaseModel):
    name: str
    age: int


@router.post(
    "/random",
    tags=["Random"],
    summary="Returns Random Shit",
)
def RandomHandler(random_input: RandomInput):
    return {
        "name": "Hey, " + random_input.name,
        "age": random_input.age,
    }


#
