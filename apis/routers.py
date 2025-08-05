from fastapi import APIRouter, Header, HTTPException, status

from apis.schema import TakeDiamondModel
from apis.functions import take_diamond
from security import SECURITY

router = APIRouter()


items_list =[
    {
        'id': 1,
        'name': 'Diamond×50+5'
    },
    {
        'id': 2,
        'name': 'Diamond×150+15'
    },
    {
        'id': 3,
        'name': 'Diamond×250+25'
    },
    {
        'id': 4,
        'name': 'Diamond×500+65'
    },
    {
        'id': 5,
        'name': 'Diamond×78+8'
    },
    {
        'id': 6,
        'name': 'Diamond×156+16'
    },
    {
        'id': 7,
        'name': 'Diamond×234+23'
    },
    {
        'id': 8,
        'name': 'Diamond×625+81'
    },
    {
        'id': 9,
        'name': 'Diamond×1860+335'
    },
    {
        'id': 10,
        'name': 'Diamond×3099+589'
    },
    {
        'id': 11,
        'name': 'Diamond×4649+883'
    },
    {
        'id': 12,
        'name': 'Diamond×7740+1548'
    },
    {
        'id': 13,
        'name': 'Passagem do crepúsculo'
    }
]

@router.get("/items/")
async def read_item():
    return items_list


@router.post("/items/")
async def read_item(
        teke_diamond_data: TakeDiamondModel,
        x_api_key: str = Header(..., alias="X-API-KEY")
):
    if x_api_key != SECURITY.X_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    item_id = teke_diamond_data.item_id
    user_id = teke_diamond_data.user_id
    server_id = teke_diamond_data.server_id
    return await take_diamond(user_id, item_id, server_id)