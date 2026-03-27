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
        
        self.font_paths = [
            os.path.join(self.font_dir, "Inter-Bold.ttf"),
            os.path.join(self.font_dir, "Inter-Regular.ttf"),
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]

    def _get_fonts(self, scale: float):
        def load_font(size, bold=False):
            scaled_size = int(size * scale)
            for path in self.font_paths:
                try:
                    return ImageFont.truetype(path, scaled_size)
                except Exception:
                    continue
            return ImageFont.load_default()

        return {
            'title': load_font(72, True),
            'subtitle': load_font(36),
            'section': load_font(28, True),
            'body': load_font(22),
            'small': load_font(18),
            'extra_small': load_font(14)
        }

    def generate_dashboard(self, data: LabReportData, width: int = 1920, height: int = 1080) -> Image.Image:
        scale = width / 1920.0
        fonts = self._get_fonts(scale)
        
        img = Image.new('RGB', (width, height), color=self.bg_color)
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Add subtle radial gradient background or ambient glow
        self._draw_ambient_glow(draw, width, height, scale)
        
        # 1. Header Section
        self._draw_header(draw, data, width, fonts, scale)
        
        # 2. Left Panel: Cannabinoids
        self._draw_cannabinoids(draw, data.cannabinoids, fonts, scale)
        
        # 3. Center: Visual (Flower/Placeholder)
        self._draw_center_visual(img, draw, width, height, scale)
        
        # 4. Right Panel: Terpenes
        self._draw_terpenes(draw, data.terpenes, fonts, scale)
        
        # 5. Bottom: Info Strip
        self._draw_footer(draw, data, width, height, fonts, scale)
        
        # 6. Watermark
        self._draw_watermark(draw, width, height, fonts, scale)
        
        return img

    def _draw_watermark(self, draw, width, height, fonts, scale):
        text = "POWERED BY STRAINAI"
        draw.text((width - int(300 * scale), height - int(60 * scale)), text, font=fonts['small'], fill=(255, 255, 255, 80))

    def _draw_ambient_glow(self, draw, width, height, scale):
        center_x, center_y = width // 2, height // 2
        glow_radius = int(500 * scale)
        for r in range(glow_radius, 0, int(-10 * scale)):
            alpha = int(30 * (1 - r/glow_radius))
            draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], 
                         fill=(138, 43, 226, alpha))

    def _draw_header(self, draw, data, width, fonts, scale):
        title = data.strain_name.upper()
        subtitle = f"{data.strain_type or 'HYBRID'} | {data.dominance or 'BALANCED'}"
        
        title_bbox = draw.textbbox((0, 0), title, font=fonts['title'])
        title_w = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_w) // 2, int(80 * scale)), title, font=fonts['title'], fill=self.text_color)
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=fonts['subtitle'])
        subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(((width - subtitle_w) // 2, int(180 * scale)), subtitle, font=fonts['subtitle'], fill=self.accent_color)

    def _draw_cannabinoids(self, draw, cannabinoids, fonts, scale):
        x, y = int(100 * scale), int(280 * scale)
        w, h = int(450 * scale), int(620 * scale)
        self._draw_glass_card(draw, x, y, w, h, "CANNABINOID PROFILE", fonts, scale)
        
        y_offset = y + int(100 * scale)
        for i, cb in enumerate(cannabinoids[:8]):
            draw.text((x + int(30 * scale), y_offset), f"{cb.name}", font=fonts['section'], fill=self.text_color)
            draw.text((x + w - int(120 * scale), y_offset), f"{cb.value}{cb.unit}", font=fonts['section'], fill=self.accent_color)
            
            draw.rectangle([x + int(30 * scale), y_offset + int(45 * scale), x + w - int(30 * scale), y_offset + int(55 * scale)], fill=(50, 50, 60, 255))
            bar_w = (cb.value / 35.0) * (w - int(60 * scale))
            bar_w = min(bar_w, w - int(60 * scale))
            draw.rectangle([x + int(30 * scale), y_offset + int(45 * scale), x + int(30 * scale) + bar_w, y_offset + int(55 * scale)], fill=self.accent_color)
            
            y_offset += int(65 * scale)

    def _draw_terpenes(self, draw, terpenes, fonts, scale):
        x, y = int(1370 * scale), int(280 * scale)
        w, h = int(450 * scale), int(620 * scale)
        self._draw_glass_card(draw, x, y, w, h, "TERPENE PROFILE", fonts, scale)
        
        y_offset = y + int(100 * scale)
        for i, terp in enumerate(terpenes[:10]):
            draw.text((x + int(30 * scale), y_offset), f"{i+1}. {terp.name}", font=fonts['body'], fill=self.text_color)
            draw.text((x + w - int(100 * scale), y_offset), f"{terp.value}{terp.unit}", font=fonts['body'], fill=self.accent_color)
            y_offset += int(48 * scale)

    def _draw_center_visual(self, img, draw, width, height, scale):
        pass

    def _draw_footer(self, draw, data, width, height, fonts, scale):
        y = height - int(120 * scale)
        items = [
            f"ORIGIN: {data.origin or 'N/A'}",
            f"LAB: {data.lab_name or 'N/A'}",
            f"BATCH: {data.batch or 'N/A'}",
            f"TEST DATE: {data.test_date or 'N/A'}",
            f"GENETICS: {data.genetics or 'N/A'}"
        ]
        info_text = "  |  ".join(items)
        
        bbox = draw.textbbox((0, 0), info_text, font=fonts['small'])
        text_w = bbox[2] - bbox[0]
        draw.text(((width - text_w) // 2, y), info_text, font=fonts['small'], fill=self.muted_text_color)

    def _draw_glass_card(self, draw, x, y, w, h, title, fonts, scale):
        draw.rounded_rectangle([x, y, x + w, y + h], radius=int(30 * scale), fill=self.card_bg, outline=(100, 100, 120, 100), width=max(1, int(2 * scale)))
        draw.text((x + int(30 * scale), y + int(30 * scale)), title, font=fonts['section'], fill=self.muted_text_color)

