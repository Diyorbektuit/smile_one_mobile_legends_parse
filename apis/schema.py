from pydantic import BaseModel


class TakeDiamondModel(BaseModel):
    item_id: int
    user_id: int
    server_id: int