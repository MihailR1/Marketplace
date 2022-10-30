from enum import Enum


class ProductSortingTypes(Enum):
    price_from_min_to_max = 'price_from_min_to_max'
    price_from_max_to_min = 'price_from_max_to_min'

    def readable_values(self):
        if self == ProductSortingTypes.price_from_min_to_max:
            return 'Сначала недорогие'
        elif self == ProductSortingTypes.price_from_max_to_min:
            return 'Сначала дорогие'
