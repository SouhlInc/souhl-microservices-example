from typing import List

import strawberry

from lib.gql_shared.books_reviews_shared import ExternalValue


@strawberry.federation.type(keys=["id"])
class Book:
    id: str
    external_value: ExternalValue
    title: str


def get_all_books() -> List[Book]:
    return [
        Book(
            id="book_1",
            external_value=ExternalValue.EXTERNAL_VALUE1,
            title="The Dark Tower",
        ),
        Book(
            id="book_2",
            external_value=ExternalValue.EXTERNAL_VALUE2,
            title="The Hobbit",
        ),
    ]


@strawberry.type
class Query:
    all_books: List[Book] = strawberry.field(resolver=get_all_books)


schema = strawberry.federation.Schema(query=Query, enable_federation_2=True)
