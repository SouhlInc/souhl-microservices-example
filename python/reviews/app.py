from typing import List

import strawberry
from fastapi import FastAPI
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext, GraphQLRouter
from strawberry.types import Info


def new_reviews_by_book_loader() -> DataLoader[str, List["Review"]]:
    async def load_reviews_by_book_ids(
        book_ids: List[str],
    ) -> List[List["Review"]]:
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
    print(f"Loading reviews for book: {root.id}")
    return await info.context.reviews_by_book_loader.load(root.id)


class GraphqlContext(BaseContext):
    def __init__(
        self,
        reviews_by_book_loader: DataLoader[str, List["Review"]],
    ):
        self.reviews_by_book_loader = reviews_by_book_loader


def new_graphql_context() -> GraphqlContext:
    return GraphqlContext(
        reviews_by_book_loader=new_reviews_by_book_loader(),
    )


@strawberry.type
class Review:
    id: str
    body: str


@strawberry.federation.type(keys=["id"])
class Book:
    id: str
    reviews_count: int
    reviews: List[Review] = strawberry.field(resolver=reviews_by_book)

    # BookはBookサービスのentityであるが、ReviewsサービスにしかないBookのフィールドがあるならば、resolve_referenceで取得する
    # keysにしていされているフィールド(今回はid)や、reviewsのようなresolverが直接指定されているフィールドしかないなら、resolve_referenceは書かなくて良い。
    @classmethod
    def resolve_reference(cls, id: str):
        # here we could fetch the book from the database
        # or even from an API
        return Book(id=id, reviews_count=3)


@strawberry.type
class Query:
    # this field is not used in the supergraph schema
    _hi: str = strawberry.field(resolver=lambda: "Hello World!")


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
