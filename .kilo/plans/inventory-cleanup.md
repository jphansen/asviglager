# Inventory Management Cleanup Plan

## 1. Rename "Product" to "Item" everywhere

### 1.1 Model
- Rename `product.dart` → `item.dart`
- Rename class `Product` → `Item`
- Rename all `Product` references across the codebase (imports, variable names, method names)

### 1.2 Screens
- Rename `products_screen.dart` → `items_screen.dart`
- Rename `new_product_screen.dart` → `new_item_screen.dart`
- Rename `edit_product_screen.dart` → `edit_item_screen.dart`
- Update "Products" → "Items", "New Product" → "New Item", "Edit Product" → "Edit Item"

### 1.3 Services
- Rename `product_service.dart` → `item_service.dart`
- Rename class `ProductService` → `ItemService`

### 1.4 Home screen
- Update menu button label from "Products" → "Items", "New Product" → "New Item"

## 2. Flatten container hierarchy

Simplify the conceptual model so that an Item is assigned to a Container, which is at a Location. Remove the "Warehouse" top-level from the user-facing container selection flow.

- Retain the `Warehouse` model and `WarehouseType` enum (backend may still need them)
- Refactor `ContainerSelector` to present a flatter, simpler picker: first select Location, then Container (skip Warehouse level)
- Update `ContainerMemory` if needed

## 3. Remove "Type" field from UI (keep auto-assigned)

- Remove `type` from `Item.toJson()` (backend can default it)
- Remove "Type" display from item detail dialog in `items_screen.dart` (currently `_showProductDetails`)
- Keep `type: '0'` (auto-assigned when creating) — remove the field from the create/edit form entirely
- Remove `type` from the `Item` / `Product` model constructor signature (keep it as optional, defaulting to '0')
- Remove `type` display from `toJson()`

## 4. Add "Category" field

### 4.1 Model changes
- Add `String? category` to `Item` model (after `label`)
- Add to `fromJson` / `toJson`

### 4.2 Category list management
- Create a `CategoryService` or add methods to `ItemService`:
  - `getCategories()` — fetch list of all distinct categories from backend or a dedicated endpoint
- Store a local cache of categories

### 4.3 UI: New Item screen
- After "Product Name" field, add a `CategoryFormField` widget:
  - Shows an `Autocomplete` with suggestions from existing categories
  - Allows free-text input — if the user types a new category, it persists as a new value
  - On submit, new categories are added to the list

### 4.4 UI: Edit Item screen
- Same Category autocomplete field, pre-filled with existing category if set

### 4.5 UI: Items list
- Display category in the item card subtitle if set

## 5. Remove "Stock Management" section

### 5.1 Home screen
- Remove the "Stock Management" `_MenuButton` from `home_screen.dart`
- Remove import of `stock_screen.dart`

### 5.2 Stock screen
- Remove `stock_screen.dart` entirely (or keep as dead code initially, but remove the route)

### 5.3 Stock management from Products/Items screen
- The item detail dialog (`_showProductDetails` / renamed to `_showItemDetails`) already allows viewing stock info
- The edit screen already allows assigning a container (stock is updated via `updateStock`)
- Keep stock edit functionality in the item edit screen — stock management happens there

## 6. Expand search to support container/location

### 6.1 Items screen search
- Update the search `TextField` hint text to indicate container/location search
- Modify `ProductService.getProducts` to pass the search query — currently it already does, but the backend may need to support container/location search
- Add client-side filtering fallback: after loading products, also filter locally by container ref/name if the backend search doesn't cover it
- Ensure the search queries include `stock_warehouse` keys (container refs) and loaded container paths

### 6.2 Backend consideration
- The search query is already sent to the backend API. If the backend already supports searching by container, this is done.
- Otherwise, implement client-side filtering: load all products, then filter where any container ref or path label contains the search query.

## 7. Show thumbnail instead of text initials in item list

### 7.1 Items list (`items_screen.dart` → currently `products_screen.dart`)
- In the `ListTile` `leading` widget:
  - If `item.photos` is not empty, load the first photo thumbnail (async) and display as a rounded image
  - If no photo, show the current gradient + text initials (fallback)
- Use the existing `_loadPhoto` / `_buildPhotoThumbnail` pattern, but adapted for the list tile leading position (smaller, 48x48 or similar)

## 8. Files to modify (summary)

| File | Action |
|------|--------|
| `lib/models/product.dart` | Rename to `item.dart`, rename Product→Item, add category field, remove type from toJson |
| `lib/models/warehouse.dart` | No changes needed (backend still uses hierarchy) |
| `lib/services/product_service.dart` | Rename to `item_service.dart`, rename ProductService→ItemService |
| `lib/screens/products_screen.dart` | Rename to `items_screen.dart`, update labels, add thumbnail, expand search |
| `lib/screens/new_product_screen.dart` | Rename to `new_item_screen.dart`, add Category field, remove Type |
| `lib/screens/edit_product_screen.dart` | Rename to `edit_item_screen.dart`, add Category field, remove Type |
| `lib/screens/home_screen.dart` | Rename menu items, remove Stock Management button |
| `lib/screens/stock_screen.dart` | Remove or mark unused |
| `lib/widgets/container_selector.dart` | Simplify to Location+Container only |
| `lib/config/api_config.dart` | Possibly add category endpoint |

## 9. Implementation order

1. Model changes (rename Product→Item, add category, remove type from UI fields)
2. Service renames
3. Widget changes (ContainerSelector simplification)
4. Screen renames and updates (ItemsScreen, NewItemScreen, EditItemScreen)
5. Home screen updates
6. Remove Stock Management screen
7. Expand search + thumbnail
8. Test & verify
