# Setting Up LemonSqueezy Products for Asset Library

This guide shows you how to structure your products in LemonSqueezy so the API can find and deliver them correctly.

---

## 🎯 Overview

The API needs specific metadata on each product to:
- Categorize assets (Furniture, Studio, etc.)
- Determine asset type (3D Models, Scenes, etc.)
- Control access by plan (Free, Basic, Premium)
- Provide thumbnail images

---

## 📦 Product Structure

Each asset should be a **Product** in LemonSqueezy with one or more **Files** attached.

### Example Product Setup

**Product Name:** Modern Chair 3D Model  
**Description:** Contemporary dining chair with fabric seat  
**Files:** 
- Modern_Chair.blend (main file)
- Modern_Chair_Thumbnail.png (preview image)

---

## 🏷️ Adding Custom Metadata

LemonSqueezy doesn't have built-in fields for custom metadata, so we have two options:

### Option 1: Use Product Description (JSON Block)

Add a JSON block in the product description:

```markdown
Contemporary dining chair with fabric seat and wooden legs.

<!-- METADATA
{
  "category": "Furniture",
  "asset_type": "3D_MODELS",
  "plan_required": "Free",
  "thumbnail_url": "https://your-cdn.com/thumbnails/chair.png"
}
-->
```

Then update the API's `parse_lemonsqueezy_file_to_asset()` function to extract this:

```python
def parse_lemonsqueezy_file_to_asset(file_data: dict) -> Optional[Asset]:
    attributes = file_data.get("attributes", {})
    description = attributes.get("description", "")
    
    # Extract metadata from description
    import re
    import json
    
    meta = {}
    match = re.search(r'<!-- METADATA\n(.*?)\n-->', description, re.DOTALL)
    if match:
        try:
            meta = json.loads(match.group(1))
        except:
            pass
    
    # Rest of the function...
```

### Option 2: Use Naming Convention

Name your files with metadata in the filename:

```
[CATEGORY]_[TYPE]_[PLAN]_AssetName.blend

Examples:
Furniture_3D_MODELS_Free_ModernChair.blend
Studio_3D_SCENES_Premium_PhotoStudio.blend
Natural_GOBOS_Basic_LeafPattern.png
```

Then parse the filename:

```python
def parse_lemonsqueezy_file_to_asset(file_data: dict) -> Optional[Asset]:
    attributes = file_data.get("attributes", {})
    filename = attributes.get("name", "")
    
    # Parse filename: Category_Type_Plan_Name.ext
    parts = filename.replace(".blend", "").split("_")
    
    if len(parts) >= 4:
        category = parts[0]
        asset_type = parts[1]
        plan_required = parts[2]
        name = "_".join(parts[3:]).replace("_", " ")
    else:
        # Fallback to defaults
        category = "Uncategorized"
        asset_type = "3D_MODELS"
        plan_required = "Free"
        name = filename
    
    # Rest of the function...
```

### Option 3: Use External Database (Most Flexible)

Store asset metadata in a separate database (like Supabase, Airtable, or your own DB):

**Airtable Example:**

| LemonSqueezy File ID | Category | Asset Type | Plan Required | Thumbnail URL |
|---------------------|----------|------------|---------------|---------------|
| 123456 | Furniture | 3D_MODELS | Free | https://... |
| 123457 | Studio | 3D_SCENES | Premium | https://... |

Then query your database in the API:

```python
import airtable

async def parse_lemonsqueezy_file_to_asset(file_data: dict) -> Optional[Asset]:
    file_id = file_data.get("id")
    
    # Fetch metadata from Airtable
    table = airtable.Airtable('base_id', 'table_name', api_key='your_key')
    records = table.get_all(formula=f"{{LemonSqueezy File ID}}='{file_id}'")
    
    if records:
        meta = records[0]['fields']
        # Use meta data...
```

---

## 📋 Required Metadata Fields

Each asset needs these fields:

### `category` (string)
The subcategory within the asset type.

**Examples:**
- For 3D Models: "Furniture", "Decoration", "Electronics", "Architecture"
- For Scenes: "Studio", "Interior", "Exterior", "Abstract"
- For Gobos: "Architectural", "Natural", "Abstract", "Geometric"
- For Geometry Nodes: "Nature", "Architecture", "Utility", "Effects"
- For Mockups: "Electronics", "Print", "Product", "Packaging"

### `asset_type` (string)
The main category. Must be one of:

- `3D_MODELS`
- `3D_SCENES`
- `GOBOS`
- `GEOMETRY_NODES`
- `3D_MOCKUPS`
- `3D_ANIMATED_MOCKUPS`
- `ADDONS`

### `plan_required` (string)
Minimum subscription plan needed. Must be one of:

- `Free`
- `Basic`
- `Premium`

### `thumbnail_url` (string, optional)
URL to preview image. Can be:
- Hosted on your own CDN (Cloudflare R2, AWS S3)
- Uploaded as a separate file in LemonSqueezy
- Generated automatically from 3D renders

---

## 🖼️ Thumbnail Images

### Option A: Separate LemonSqueezy Files

Upload thumbnail as a second file in the same product:

**Files in Product:**
1. Modern_Chair.blend (main asset)
2. Modern_Chair_Thumb.png (thumbnail)

Then in your API, match thumbnails by naming convention:

```python
# When fetching files from LemonSqueezy
files = await fetch_lemonsqueezy_files()

# Group files by product
products = {}
for file in files:
    product_id = file['relationships']['variant']['data']['id']
    
    if product_id not in products:
        products[product_id] = {'main': None, 'thumbnail': None}
    
    if file['attributes']['name'].endswith('_Thumb.png'):
        products[product_id]['thumbnail'] = file['attributes']['download_url']
    else:
        products[product_id]['main'] = file
```

### Option B: External CDN

Host thumbnails on:
- **Cloudflare R2** (cheap, fast)
- **AWS S3** (reliable)
- **Backblaze B2** (affordable)
- Your website

Upload with consistent naming:
```
https://cdn.stylarx.com/thumbnails/modern-chair.png
https://cdn.stylarx.com/thumbnails/coffee-table.png
```

Then reference in metadata:
```json
{
  "thumbnail_url": "https://cdn.stylarx.com/thumbnails/modern-chair.png"
}
```

### Option C: Generate from Blender

Create an automated render script:

```python
import bpy

def render_thumbnail(blend_file, output_path):
    # Load file
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    
    # Set up camera
    # Render thumbnail
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
```

---

## 📁 Recommended File Structure

### For 3D Models
```
Product: Modern Chair
Files:
  - Modern_Chair.blend (main file, 5-20 MB)
  - Modern_Chair_Thumb.png (512x512 px, <500 KB)
Metadata:
  - category: "Furniture"
  - asset_type: "3D_MODELS"
  - plan_required: "Free"
```

### For Scenes
```
Product: Photo Studio Setup
Files:
  - Studio_Setup.blend (main file, 50-200 MB)
  - Studio_Thumb.png (1920x1080 px, <1 MB)
Metadata:
  - category: "Studio"
  - asset_type: "3D_SCENES"
  - plan_required: "Premium"
```

### For Gobos
```
Product: Window Frame Gobo
Files:
  - Window_Frame.png (4K, <2 MB)
  - Window_Frame_Thumb.png (512x512 px, <200 KB)
Metadata:
  - category: "Architectural"
  - asset_type: "GOBOS"
  - plan_required: "Basic"
```

### For Geometry Nodes
```
Product: Procedural Grass
Files:
  - Grass_GeoNodes.blend (node tree, 1-5 MB)
  - Grass_Thumb.png (512x512 px, <500 KB)
Metadata:
  - category: "Nature"
  - asset_type: "GEOMETRY_NODES"
  - plan_required: "Basic"
```

### For Addons
```
Product: Quick Render Tools
Files:
  - quick_render_tools.zip (addon zip, 1-10 MB)
  - QuickRender_Thumb.png (512x512 px, <300 KB)
Metadata:
  - category: "Workflow"
  - asset_type: "ADDONS"
  - plan_required: "Premium"
```

---

## ✅ Checklist for Each Product

- [ ] Product created in LemonSqueezy
- [ ] Main asset file uploaded
- [ ] Thumbnail image uploaded or linked
- [ ] Metadata added (category, asset_type, plan_required)
- [ ] File naming is consistent
- [ ] Thumbnail is high quality but small file size
- [ ] Product is associated with correct variant/price
- [ ] Tested download URL works

---

## 🔄 Bulk Upload Script

If you have many assets, automate uploads with LemonSqueezy API:

```python
import httpx

async def create_product(name, category, asset_type, plan, file_path):
    """Create product in LemonSqueezy via API"""
    async with httpx.AsyncClient() as client:
        # 1. Create product
        product_response = await client.post(
            "https://api.lemonsqueezy.com/v1/products",
            headers={"Authorization": f"Bearer {LEMONSQUEEZY_API_KEY}"},
            json={
                "data": {
                    "type": "products",
                    "attributes": {
                        "name": name,
                        "description": f"<!-- METADATA\n{json.dumps({'category': category, 'asset_type': asset_type, 'plan_required': plan})}\n-->"
                    }
                }
            }
        )
        
        # 2. Upload file
        # 3. Add to store
```

---

## 🎉 You're Ready!

Once your products are set up with metadata:
1. The API will automatically fetch and categorize them
2. Users will see them in the Blender addon
3. Downloads will work seamlessly

Test with the `test_api.py` script to verify everything works!
