from pydantic import BaseModel

class MessageCreate(BaseModel):
    patient_id: str
    receiver_user_id: str
    message_text: str
