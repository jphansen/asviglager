# Inventory Management Cleanup - Todo List

## Overview
Flatten and simplify the inventory management application:
- Rename Product → Item
- Simplify container hierarchy: Item → Container → Location
- Remove "Type" field from UI (keep auto-assigned)
- Add "Category" field with autocomplete + free-text
- Remove "Stock Management" screen
- Expand search to support container/location
- Show photo thumbnails instead of text initials

---

## Tasks

### 1. Model Changes
- [ ] Rename `product.dart` → `item.dart`
- [ ] Rename class `Product` → `Item`
- [ ] Add `String? category` field to Item model
- [ ] Remove `type` from `toJson()` (keep in model for backend compatibility)
- [ ] Update `fromJson` / `toJson` to handle category

### 2. Service Changes
- [ ] Rename `product_service.dart` → `item_service.dart`
- [ ] Rename class `ProductService` → `ItemService`
- [ ] Add `CategoryService` for fetching/managing categories
- [ ] Update API endpoints if needed

### 3. Widget Changes
- [ ] Simplify `ContainerSelector`: Location → Container (skip Warehouse level)
- [ ] Update `ContainerMemory` if needed

### 4. Screen Changes
- [ ] Rename `products_screen.dart` → `items_screen.dart`
- [ ] Update all "Product" labels to "Item"
- [ ] Add photo thumbnails in item list (instead of text initials)
- [ ] Expand search to filter by container ref/location
- [ ] Rename `new_product_screen.dart` → `new_item_screen.dart`
- [ ] Add Category autocomplete field (after Item Name)
- [ ] Remove Type field from UI
- [ ] Rename `edit_product_screen.dart` → `edit_item_screen.dart`
- [ ] Add Category field to edit screen
- [ ] Remove Type field from UI

### 5. Home Screen
- [ ] Rename "Products" → "Items"
- [ ] Rename "New Product" → "New Item"
- [ ] Remove "Stock Management" menu button
- [ ] Remove import of `stock_screen.dart`

### 6. Remove Stock Management
- [ ] Delete `stock_screen.dart`
- [ ] Ensure no other references to it

### 7. API Configuration
- [ ] Add category endpoint to `api_config.dart` if needed

### 8. Testing
- [ ] Verify all imports are updated
- [ ] Test item creation with category
- [ ] Test item editing with category
- [ ] Test search by container/location
- [ ] Test photo thumbnails in list
- [ ] Verify build compiles cleanly

---

## Implementation Order
1. Model changes (item.dart)
2. Service renames (item_service.dart, category_service.dart)
3. Widget changes (container_selector.dart)
4. Screen renames and updates
5. Home screen updates
6. Remove stock_screen.dart
7. Test & verify

---

## Notes
- Keep `type` field in model for backend compatibility, but don't show/edit in UI
- Category should be autocomplete with free-text option
- Search should work on container ref (e.g., "C_203") and location names
- Thumbnails should be small (48x48 or similar) in list view
- Fallback to text initials if no photo available
