from pydantic import BaseModel


ERROR_REPLY_TEXT="哎呀，我被这个问题难住了！我会继续努力学习的~"

class DifyResponse(BaseModel):
    type: str
    data: object

    @classmethod
    def to_text(cls, data: str):
        return cls(type="text", data=data)

    @classmethod
    def to_data(cls, data: object):
        return cls(type="data", data=data)

    @classmethod
    def to_url(cls, data: str):
        return cls(type="url", data=data)

    @classmethod
    def not_found_data(cls):
        return cls(type="text", data=ERROR_REPLY_TEXT)