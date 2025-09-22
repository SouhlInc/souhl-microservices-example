from typing import List

import strawberry
from fastapi import FastAPI
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext, GraphQLRouter
from strawberry.types import Info


def new_reviews_by_book_loader() -> DataLoader[str, List["Review"]]:
    async def load_reviews_by_book_ids(
        book_ids: List[str],  # 1, 2, 3
    ) -> List[
        List["Review"]
    ]:  # [[review1_1, review1_2, review1_3], [review2_1, review2_2, review2_3], [review3_1, review3_2, review3_3]]
        print(f"Loading reviews for books: {book_ids}")

        reviews_chunks: List[List["Review"]] = []
        for book_id in book_ids:
            reviews: List["Review"] = []
            for id_ in range(3):
                reviews.append(
                    Review(id=str(id_) + "-" + book_id, body=f"A review for {id_}")
                )
            reviews_chunks.append(reviews)
        return reviews_chunks

    return DataLoader(load_fn=load_reviews_by_book_ids)


async def reviews_by_book(
    root: "Book",
    info: Info["GraphqlContext", None],
) -> List["Review"]:
    print(f"Loading reviews for book: id={root.id}")
    return await info.context.reviews_by_book_loader.load(root.id)


def new_books_by_book_id_loader() -> DataLoader[str, int]:
    async def load_reviews_count_by_book_ids(
        book_ids: List[str],
    ) -> List["Book"]:
        print(f"Loading books for book ids: {book_ids}")
        return [
            Book(id=book_id, reviews_count=3, good_reviews_count=2)
            for book_id in book_ids
        ]

    return DataLoader(load_fn=load_reviews_count_by_book_ids)


class GraphqlContext(BaseContext):
    def __init__(
        self,
        reviews_by_book_loader: DataLoader[str, List["Review"]],
        books_by_book_id_loader: DataLoader[str, "Book"],
    ):
        self.reviews_by_book_loader = reviews_by_book_loader
        self.books_by_book_id_loader = books_by_book_id_loader


def new_graphql_context() -> GraphqlContext:
    return GraphqlContext(
        reviews_by_book_loader=new_reviews_by_book_loader(),
        books_by_book_id_loader=new_books_by_book_id_loader(),
    )


@strawberry.type
class Review:
    id: str
    body: str


@strawberry.federation.type(keys=["id"])
class Book:
    id: str
    # external_value: ExternalValue = strawberry.federation.field(directives=[External()])
    reviews_count: int
    good_reviews_count: int
    reviews: List[Review] = strawberry.federation.field(
        resolver=reviews_by_book,
        directives=[
            # Requires(fields="externalValue")
        ],
    )

    # NOTE: external_valueを使うようにしたら、resolve_referenceが使えなくなった。
    # BookはBookサービスのentityであるが、ReviewsサービスにしかないBookのフィールドがあるならば、resolve_referenceで取得する
    @classmethod
    async def resolve_reference(cls, id: str, info: Info["GraphqlContext", None]):
        # here we could fetch the book from the database
        # or even from an API

        # resolver reference も試しに data loader で取得してみる
        print(f"Resolving reference for book: id={id}")
        return await info.context.books_by_book_id_loader.load(id)


@strawberry.type
class Query:
    hi: str = strawberry.field(resolver=lambda: "Hello World!")


schema = strawberry.federation.Schema(
    query=Query, types=[Book, Review], enable_federation_2=True
)

router = GraphQLRouter(
    schema,
    context_getter=new_graphql_context,
    allow_queries_via_get=False,
)

app = FastAPI()
app.include_router(router, prefix="/graphql")
