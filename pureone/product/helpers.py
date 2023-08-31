from typing import Any

filter_mappings = {
    "is_featured": {
        "filter": {
            "is_featured": True,
        },
    },
    "top_selling": {
        "order_by": "-order_count",
    },
    "top_rated": {
        "filter": {
            "average_rating__gt": 0,
        },
        "order_by": "-average_rating",
    },
    "low_price": {
        "order_by": "price" ,
    },
    "high_price": {
        "order_by": "-price", 
    },
    "discount": {
        "order_by": "-discount",
    },
    "new": {
        "order_by": "-created_at" ,
    },
    "az": {
        "order_by": "display_name", 
    }
}

def filter_product(products: Any, filter_query: str) -> Any:
    """
    Function to apply filters to products

    Parameters
    ----------
    products : Any
        products queryset
    filter_query : str
        name which will be present as a key in filter_mappings dictionary

    Returns
    -------
    Any
        Filtered products
    """
    filter_mapping = filter_mappings.get(filter_query)
    if not filter_mapping:
        return products
    if "filter" in filter_mapping:
        products = products.filter(**filter_mapping.get("filter", {}))
    
    if "order_by" in filter_mapping:
        products = products.order_by(filter_mapping.get("order_by", "-id"))

    return products