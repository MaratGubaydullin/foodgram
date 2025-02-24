def generate_shopping_list(ingredients):
    """Генерация текстового списка покупок.

    Принимает QuerySet ингредиентов с аннотацией sum.

    Возвращает форматированную строку.
    """
    return '\n'.join(
        'Суммированный список ингридиентов:'
        f'{ingridient["ingredient__name"]} - {ingridient["sum"]} '
        f'({ingridient["ingredient__measurement_unit"]})'
        for ingridient in ingredients
    )
