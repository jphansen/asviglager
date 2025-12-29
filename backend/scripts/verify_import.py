#!/usr/bin/env python3
"""
Verify MongoDB import results
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


async def verify():
    client = AsyncIOMotorClient('mongodb://asviglager:Horsens2025@172.32.0.3:27017')
    db = client.asviglager
    
    # Count documents
    count = await db.products.count_documents({})
    active = await db.products.count_documents({'deleted': False})
    deleted = await db.products.count_documents({'deleted': True})
    
    print(f'Total products in MongoDB: {count}')
    print(f'  Active: {active}')
    print(f'  Deleted: {deleted}')
    
    # Get sample product
    sample = await db.products.find_one({'ref': '100014'})
    if sample:
        print(f'\nSample product (ref: 100014):')
        print(f'  label: {sample["label"]}')
        print(f'  price: {sample.get("price")} ({type(sample.get("price")).__name__})')
        print(f'  cost_price: {sample.get("cost_price")} ({type(sample.get("cost_price")).__name__})')
        print(f'  price_ttc: {sample.get("price_ttc")} ({type(sample.get("price_ttc")).__name__})')
        print(f'  pmp: {sample.get("pmp")} ({type(sample.get("pmp")).__name__})')
    
    # Check a few more products for price field types
    print(f'\nChecking price field types across products...')
    products_with_prices = await db.products.find(
        {'price': {'$ne': None}},
        {'ref': 1, 'label': 1, 'price': 1}
    ).limit(5).to_list(5)
    
    for p in products_with_prices:
        print(f'  {p["ref"]}: price={p["price"]} ({type(p["price"]).__name__})')
    
    client.close()


if __name__ == '__main__':
    asyncio.run(verify())
