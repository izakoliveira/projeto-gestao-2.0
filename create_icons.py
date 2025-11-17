from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename, text="SGP"):
    # Criar em resolução muito alta para máxima qualidade
    scale = 16
    large_size = size * scale
    
    # Criar imagem RGBA
    img = Image.new('RGBA', (large_size, large_size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Fundo azul sólido - retângulo com cantos arredondados
    radius = large_size // 8  # Cantos levemente arredondados
    draw.rounded_rectangle(
        [0, 0, large_size, large_size],
        radius=radius,
        fill=(0, 120, 212, 255)  # Azul Microsoft
    )
    
    # Adicionar texto "SGP" - estilo simples e limpo
    try:
        # Texto bem grande e legível
        font_size = int(large_size // 1.9)
        fonts = [
            "C:\\Windows\\Fonts\\segoeuib.ttf",  # Segoe UI Bold
            "C:\\Windows\\Fonts\\ariblk.ttf",     # Arial Black
            "C:\\Windows\\Fonts\\arialbd.ttf",    # Arial Bold
            "arialbd.ttf"
        ]
        font = None
        for font_path in fonts:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Centralizar texto
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (large_size - text_width) // 2 - bbox[0]
    y = (large_size - text_height) // 2 - bbox[1]
    
    # Texto branco limpo - SEM sombra para estilo minimalista
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Redimensionar com LANCZOS
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Salvar
    os.makedirs('static/icons', exist_ok=True)
    img.save(f'static/icons/{filename}', quality=100, optimize=False)
    
    return img

# Criar ícones de diferentes tamanhos para PWA
icon_192 = create_icon(192, 'icon-192.png')
icon_512 = create_icon(512, 'icon-512.png')

print("✅ Ícones PNG criados com sucesso!")

# Criar ícone .ico para o instalador (múltiplos tamanhos em alta resolução)
try:
    # Criar ícones em todas as resoluções necessárias
    sizes = [16, 24, 32, 48, 64, 128, 256]
    
    print("   Gerando ícone 256x256 (base)...")
    icon_256 = create_icon(256, 'temp_256.png')
    
    # Criar lista de todas as imagens redimensionadas
    all_sizes = []
    for sz in sizes:
        if sz != 256:
            print(f"   Gerando ícone {sz}x{sz}...")
            icon_resized = create_icon(sz, f'temp_{sz}.png')
            all_sizes.append(icon_resized)
        else:
            all_sizes.append(icon_256)
    
    # Salvar o .ico com múltiplas resoluções (método correto)
    icon_256.save(
        'sgp_icon.ico',
        format='ICO',
        sizes=[(sz, sz) for sz in sizes],
        append_images=all_sizes[1:] if len(all_sizes) > 1 else []
    )
    
    # Limpar arquivos temporários
    for sz in sizes:
        temp_path = f'static/icons/temp_{sz}.png'
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    # Verificar tamanho do arquivo gerado
    import os
    ico_size = os.path.getsize('sgp_icon.ico')
    print("✅ Ícone ICO de alta qualidade criado: sgp_icon.ico")
    print(f"   Tamanho do arquivo: {ico_size:,} bytes")
    print(f"   Resoluções incluídas: {', '.join([f'{sz}x{sz}' for sz in sizes])}")
except Exception as e:
    print(f"⚠️ Erro ao criar ICO: {e}")
    import traceback
    traceback.print_exc() 