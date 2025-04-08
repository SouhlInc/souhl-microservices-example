from typing import List

import strawberry


@strawberry.federation.type(keys=["id"])
class Book:
    id: strawberry.ID
    title: str


def get_all_books() -> List[Book]:
    return [
        Book(id=strawberry.ID("book_1"), title="The Dark Tower"),
        Book(id=strawberry.ID("book_2"), title="The Hobbit"),
    ]


@strawberry.type
class Query:
    all_books: List[Book] = strawberry.field(resolver=get_all_books)


schema = strawberry.federation.Schema(query=Query, enable_federation_2=True)
