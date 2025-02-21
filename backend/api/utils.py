def generate_shopping_list(ingredients):
    """Генерация текстового списка покупок.

    Принимает QuerySet ингредиентов с аннотацией sum.

    Возвращает форматированную строку.
    """
    return '\n'.join(
        f'{i["ingredient__name"]} - {i["sum"]} '
        f'({i["ingredient__measurement_unit"]})'
        for i in ingredients
    )
