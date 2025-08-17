
from transformers import pipeline
from PIL import Image
import io

# Use a public general-purpose model for image classification
classifier = pipeline("image-classification", model="google/vit-base-patch16-224", device=-1)

def analyze_image_bytes(image_bytes: bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return {"error": f"Cannot open image: {e}"}

    try:
        preds = classifier(image, top_k=1)
    except Exception as e:
        return {"error": f"Image classification failed: {e}", "raw_bytes_length": len(image_bytes)}

    # Only the top prediction
    if preds and len(preds) > 0:
        top_pred = preds[0]
        item_name = top_pred["label"]
        score = top_pred["score"]
    else:
        item_name = "Unknown"
        score = 0.0

    # Condition heuristic (brightness)
    try:
        grayscale = image.convert("L")
        pixels = list(grayscale.getdata())
        avg_brightness = sum(pixels) / len(pixels)
        if avg_brightness > 170:
            condition = "new"
        elif avg_brightness > 100:
            condition = "good"
        else:
            condition = "worn"
    except:
        condition = "unknown"

    # Color detection (dominant color, only hex code)
    try:
        # Ensure image is in RGB mode
        rgb_image = image.convert("RGB")
        # Resize to speed up
        small_img = rgb_image.resize((50, 50))
        pixels = list(small_img.getdata())
        # Filter out near-white and near-black pixels
        def is_not_bg(rgb):
            r, g, b = rgb
            if (r > 230 and g > 230 and b > 230):
                return False
            if (r < 30 and g < 30 and b < 30):
                return False
            return True
        filtered_pixels = [p for p in pixels if is_not_bg(p)]
        from collections import Counter
        if filtered_pixels:
            most_common = Counter(filtered_pixels).most_common(1)[0][0]
        else:
            most_common = Counter(pixels).most_common(1)[0][0]  # fallback to all pixels
        color_hex = '#%02x%02x%02x' % most_common
    except Exception as e:
        color_hex = "unknown"

    return {
        "item_name": item_name,
        "score": score,
        "condition": condition,
        "color_hex": color_hex
    }
