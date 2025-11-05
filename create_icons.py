from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename, text="SGP"):
    # Criar uma imagem com fundo gradiente azul moderno
    img = Image.new('RGB', (size, size), color='#1976d2')
    draw = ImageDraw.Draw(img)
    
    # Adicionar círculo de fundo para destaque
    margin = size // 10
    draw.ellipse([margin, margin, size-margin, size-margin], fill='#1565c0')
    
    # Adicionar texto "SGP"
    try:
        # Tentar usar fonte do sistema (em ordem de preferência)
        font_size = size // 3
        fonts = ["arialbd.ttf", "arial.ttf", "calibrib.ttf", "calibri.ttf"]
        font = None
        for font_name in fonts:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except:
                continue
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Adicionar sombra ao texto
    shadow_offset = size // 80
    draw.text((x + shadow_offset, y + shadow_offset), text, fill='#0d47a1', font=font)
    draw.text((x, y), text, fill='white', font=font)
    
    # Salvar a imagem
    os.makedirs('static/icons', exist_ok=True)
    img.save(f'static/icons/{filename}')
    
    return img

# Criar ícones de diferentes tamanhos para PWA
icon_192 = create_icon(192, 'icon-192.png')
icon_512 = create_icon(512, 'icon-512.png')

# Criar ícone .ico para o instalador (múltiplos tamanhos)
try:
    icon_16 = create_icon(16, 'temp_16.png')
    icon_32 = create_icon(32, 'temp_32.png')
    icon_48 = create_icon(48, 'temp_48.png')
    icon_64 = create_icon(64, 'temp_64.png')
    icon_128 = create_icon(128, 'temp_128.png')
    icon_256 = create_icon(256, 'temp_256.png')
    
    # Combinar todos os tamanhos em um arquivo .ico
    icon_256.save('sgp_icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    
    # Limpar arquivos temporários
    for temp_file in ['temp_16.png', 'temp_32.png', 'temp_48.png', 'temp_64.png', 'temp_128.png', 'temp_256.png']:
        temp_path = f'static/icons/{temp_file}'
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    print("✅ Ícones PNG criados com sucesso!")
    print("✅ Ícone ICO criado: sgp_icon.ico")
except Exception as e:
    print(f"⚠️ Ícones PNG criados, mas erro ao criar ICO: {e}")
    print("   (O arquivo ICO pode não ser necessário para todos os casos)") 