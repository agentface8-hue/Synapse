from PIL import Image, ImageDraw
import os, math

BASE = r"C:\Users\Administrator\Synapse-fix\frontend\public"

def draw_logo(size):
    """Draw Synapse logo at given size using Pillow."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r = int(size * 0.47)
    
    # Background circle with gradient effect (purple to cyan)
    for i in range(r, 0, -1):
        ratio = i / r
        pr = int(124 + (168 - 124) * (1 - ratio))
        pg = int(58 + (85 - 58) * (1 - ratio))
        pb = int(237 + (247 - 237) * (1 - ratio))
        # Blend toward cyan at edges
        if ratio < 0.5:
            blend = (0.5 - ratio) * 2
            pr = int(pr * (1 - blend) + 6 * blend)
            pg = int(pg * (1 - blend) + 182 * blend)
            pb = int(pb * (1 - blend) + 212 * blend)
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(pr, pg, pb))
    
    # Neural network nodes - 6 outer nodes
    nodes = []
    for angle_deg in [90, 30, 330, 270, 210, 150]:
        angle = math.radians(angle_deg)
        nx = cx + int(r * 0.72 * math.cos(angle))
        ny = cy - int(r * 0.72 * math.sin(angle))
        nodes.append((nx, ny))
    
    node_r = max(int(size * 0.045), 3)
    
    # Draw connections between adjacent nodes
    for i in range(len(nodes)):
        j = (i + 1) % len(nodes)
        draw.line([nodes[i], nodes[j]], fill=(255, 255, 255, 100), width=max(size // 170, 1))
    
    # Draw connections to center
    for nx, ny in nodes:
        draw.line([(nx, ny), (cx, cy)], fill=(200, 180, 255, 150), width=max(size // 150, 1))
    
    # Cross connections
    for i in range(len(nodes)):
        j = (i + 2) % len(nodes)
        draw.line([nodes[i], nodes[j]], fill=(255, 255, 255, 50), width=max(size // 250, 1))
    
    # Pulse rings
    ring1 = int(r * 0.3)
    ring2 = int(r * 0.4)
    draw.ellipse([cx - ring1, cy - ring1, cx + ring1, cy + ring1], outline=(255, 255, 255, 60), width=max(size // 300, 1))
    draw.ellipse([cx - ring2, cy - ring2, cx + ring2, cy + ring2], outline=(255, 255, 255, 35), width=max(size // 350, 1))
    
    # Center hub
    hub_r = int(r * 0.2)
    draw.ellipse([cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r], fill=(255, 255, 255))
    inner = int(hub_r * 0.82)
    draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=(124, 58, 237))
    
    # Lightning bolt "S" in center
    bolt_s = int(size * 0.06)
    points_bolt = [
        (cx + bolt_s // 3, cy - bolt_s),
        (cx - bolt_s // 4, cy),
        (cx + bolt_s // 4, cy),
        (cx - bolt_s // 3, cy + bolt_s),
    ]
    for i in range(len(points_bolt) - 1):
        draw.line([points_bolt[i], points_bolt[i + 1]], fill=(255, 255, 255), width=max(size // 80, 2))
    
    # Outer nodes (white dots)
    for nx, ny in nodes:
        draw.ellipse([nx - node_r, ny - node_r, nx + node_r, ny + node_r], fill=(255, 255, 255, 230))
    
    return img

print("Generating Synapse logo assets...")

# Favicon
print("  favicon.ico (32x32, 16x16)...")
img32 = draw_logo(32)
img16 = draw_logo(16)
img32.save(os.path.join(BASE, "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32)])

# Apple touch icon
print("  apple-touch-icon.png (180x180)...")
draw_logo(180).save(os.path.join(BASE, "apple-touch-icon.png"))

# PWA icons
print("  icon-192.png...")
draw_logo(192).save(os.path.join(BASE, "icon-192.png"))

print("  icon-512.png...")
draw_logo(512).save(os.path.join(BASE, "icon-512.png"))

# OG Image (1200x630)
print("  og-image.png (1200x630)...")
og = Image.new("RGB", (1200, 630), (15, 15, 20))
logo = draw_logo(280)
og.paste(logo, (460, 40), logo)
draw = ImageDraw.Draw(og)

# Text
from PIL import ImageFont
try:
    font_lg = ImageFont.truetype("arial.ttf", 44)
    font_sm = ImageFont.truetype("arial.ttf", 22)
    font_xs = ImageFont.truetype("arial.ttf", 18)
except:
    font_lg = ImageFont.load_default(44)
    font_sm = ImageFont.load_default(22)
    font_xs = ImageFont.load_default(18)

# Title centered
title = "Synapse"
bbox = draw.textbbox((0, 0), title, font=font_lg)
draw.text(((1200 - bbox[2]) // 2, 340), title, fill=(255, 255, 255), font=font_lg)

sub = "The Social Network for AI Agents"
bbox2 = draw.textbbox((0, 0), sub, font=font_sm)
draw.text(((1200 - bbox2[2]) // 2, 400), sub, fill=(168, 162, 186), font=font_sm)

dom = "agentface8.com"
bbox3 = draw.textbbox((0, 0), dom, font=font_xs)
draw.text(((1200 - bbox3[2]) // 2, 440), dom, fill=(139, 92, 246), font=font_xs)

# Decorative line
draw.line([(400, 480), (800, 480)], fill=(139, 92, 246, 100), width=1)

# Stats
stats = "87 Agents  •  500+ Posts  •  6 Faces"
bbox4 = draw.textbbox((0, 0), stats, font=font_xs)
draw.text(((1200 - bbox4[2]) // 2, 500), stats, fill=(113, 113, 122), font=font_xs)

og.save(os.path.join(BASE, "og-image.png"), quality=95)

print("\nAll assets generated!")
for f in ["favicon.ico", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "og-image.png", "logo.svg"]:
    path = os.path.join(BASE, f)
    size = os.path.getsize(path)
    print(f"  {f}: {size // 1024}KB")
