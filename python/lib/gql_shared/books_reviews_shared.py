from enum import StrEnum

import strawberry


@strawberry.enum
class ExternalValue(StrEnum):
    EXTERNAL_VALUE1 = "external_value1"
    EXTERNAL_VALUE2 = "external_value2"
