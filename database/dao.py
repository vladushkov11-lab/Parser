from sqlalchemy import select
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from database.models import Product
from database.base import connection
from datetime import timedelta
from datetime import datetime
from random import randint
import random
@connection 
def create_products(session, name, price_no_spp, price_spp, percent_spp) -> Optional[Product]:
    try:
        product = Product(
            name=name,
            price_no_spp=price_no_spp,
            price_spp=price_spp,
            percent_spp = percent_spp)
        session.add(product)
        session.commit()
        return product
    except SQLAlchemyError as e:
        session.rollback()
        return None