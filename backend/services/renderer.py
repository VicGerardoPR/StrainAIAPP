import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Optional
from models import LabReportData

class VisualRenderer:
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        self.font_dir = os.path.join(assets_dir, "fonts")
        self.image_dir = os.path.join(assets_dir, "images")
        
        # Colors - Premium Futuristic Dark Mode
        self.bg_color = (10, 10, 11)  # #0a0a0b
        self.accent_color = (138, 43, 226)  # BlueViolet
        self.text_color = (255, 255, 255)
        self.sub_text_color = (200, 200, 200)
        self.muted_text_color = (150, 150, 150)
        self.card_bg = (20, 20, 25, 180)  # semi-transparent
        
        # Initialize fonts (fallbacks)
        self.fonts = {}
        
        # System font paths to try on Mac/Linux
        font_paths = [
            os.path.join(self.font_dir, "Inter-Bold.ttf"),
            os.path.join(self.font_dir, "Inter-Regular.ttf"),
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
        
        def load_font(size, bold=False):
            for path in font_paths:
                try:
                    # PIL can handle .ttc if you don't specify index (it takes index 0)
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
            return ImageFont.load_default()

        self.fonts['title'] = load_font(72, True)
        self.fonts['subtitle'] = load_font(36)
        self.fonts['section'] = load_font(28, True)
        self.fonts['body'] = load_font(22)
        self.fonts['small'] = load_font(18)

    def generate_dashboard(self, data: LabReportData) -> Image.Image:
        # Create canvas (1920x1080 for high resolution)
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color=self.bg_color)
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Add subtle radial gradient background or ambient glow
        self._draw_ambient_glow(draw, width, height)
        
        # 1. Header Section
        self._draw_header(draw, data, width)
        
        # 2. Left Panel: Cannabinoids
        self._draw_cannabinoids(draw, data.cannabinoids)
        
        # 3. Center: Visual (Flower/Placeholder)
        self._draw_center_visual(img, draw)
        
        # 4. Right Panel: Terpenes
        self._draw_terpenes(draw, data.terpenes)
        
        # 5. Bottom: Info Strip
        self._draw_footer(draw, data, width, height)
        
        # 6. Watermark
        self._draw_watermark(draw, width, height)
        
        return img

    def _draw_watermark(self, draw, width, height):
        text = "POWERED BY STRAINAI"
        draw.text((width - 300, height - 60), text, font=self.fonts['small'], fill=(255, 255, 255, 80))

    def _draw_ambient_glow(self, draw, width, height):
        # Subtle purple glow in the center
        center_x, center_y = width // 2, height // 2
        for r in range(500, 0, -10):
            alpha = int(30 * (1 - r/500))
            draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], 
                         fill=(138, 43, 226, alpha))

    def _draw_header(self, draw, data, width):
        # Strain name
        title = data.strain_name.upper()
        subtitle = f"{data.strain_type or 'HYBRID'} | {data.dominance or 'BALANCED'}"
        
        # Centered Header
        title_bbox = draw.textbbox((0, 0), title, font=self.fonts['title'])
        title_w = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_w) // 2, 80), title, font=self.fonts['title'], fill=self.text_color)
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=self.fonts['subtitle'])
        subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(((width - subtitle_w) // 2, 160), subtitle, font=self.fonts['subtitle'], fill=self.accent_color)

    def _draw_cannabinoids(self, draw, cannabinoids):
        # Left panel card
        x, y = 100, 250
        w, h = 450, 600
        self._draw_glass_card(draw, x, y, w, h, "CANNABINOID PROFILE")
        
        # Draw bars
        y_offset = y + 100
        for i, cb in enumerate(cannabinoids[:8]):  # Limit to 8
            # Label
            draw.text((x + 30, y_offset), f"{cb.name}", font=self.fonts['section'], fill=self.text_color)
            draw.text((x + w - 100, y_offset), f"{cb.value}{cb.unit}", font=self.fonts['section'], fill=self.accent_color)
            
            # Progress bar background
            draw.rectangle([x + 30, y_offset + 40, x + w - 30, y_offset + 50], fill=(50, 50, 60, 255))
            # Progress bar fill
            bar_w = (cb.value / 35.0) * (w - 60) # Max 35% for normalization
            bar_w = min(bar_w, w - 60)
            draw.rectangle([x + 30, y_offset + 40, x + 30 + bar_w, y_offset + 50], fill=self.accent_color)
            
            y_offset += 65

    def _draw_terpenes(self, draw, terpenes):
        # Right panel card
        x, y = 1370, 250
        w, h = 450, 600
        self._draw_glass_card(draw, x, y, w, h, "TERPENE PROFILE")
        
        # Rank terpenes
        y_offset = y + 100
        for i, terp in enumerate(terpenes[:8]):
            draw.text((x + 30, y_offset), f"{i+1}. {terp.name}", font=self.fonts['body'], fill=self.text_color)
            draw.text((x + w - 100, y_offset), f"{terp.value}{terp.unit}", font=self.fonts['body'], fill=self.accent_color)
            y_offset += 55

    def _draw_center_visual(self, img, draw):
        # Placeholder or flower image
        # For now, let's just use a stylized circle/glow
        center_x, center_y = 1920 // 2, 1080 // 2
        # Future: Load flower image, crop, add glow
        pass

    def _draw_footer(self, draw, data, width, height):
        # Info strip at the bottom
        y = height - 120
        info_text = f"ORIGIN: {data.origin or 'N/A'}  |  LAB: {data.lab_name or 'N/A'}  |  BATCH: {data.batch or 'N/A'}  |  TEST DATE: {data.test_date or 'N/A'}"
        
        bbox = draw.textbbox((0, 0), info_text, font=self.fonts['small'])
        text_w = bbox[2] - bbox[0]
        draw.text(((width - text_w) // 2, y), info_text, font=self.fonts['small'], fill=self.muted_text_color)

    def _draw_glass_card(self, draw, x, y, w, h, title):
        # Draw rounded rectangle with semi-transparent fill
        draw.rounded_rectangle([x, y, x + w, y + h], radius=30, fill=self.card_bg, outline=(100, 100, 120, 100), width=2)
        # Draw section title
        draw.text((x + 30, y + 30), title, font=self.fonts['section'], fill=self.muted_text_color)
