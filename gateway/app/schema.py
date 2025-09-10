import strawberry
from typing import List

@strawberry.type
class User:
    id: str
    name: str
    email: str

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Gateway!"

schema = strawberry.Schema(query=Query)
