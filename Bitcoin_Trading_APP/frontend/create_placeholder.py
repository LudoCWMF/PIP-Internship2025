from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple placeholder image
width, height = 100, 100
image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw a circle with a "?" in the center
draw.ellipse([10, 10, 90, 90], fill=(200, 200, 200, 255), outline=(150, 150, 150, 255))

# Try to add text, but if font is not available, skip it
try:
    font = ImageFont.truetype("Arial", 40)
except:
    font = None

if font:
    draw.text((40, 30), "?", fill=(100, 100, 100, 255), font=font)
else:
    # Draw a simple question mark shape
    draw.text((40, 30), "?", fill=(100, 100, 100, 255))

# Save the image
output_path = os.path.join(os.path.dirname(__file__), "images", "placeholder.png")
image.save(output_path)
print(f"Placeholder image created at: {output_path}")