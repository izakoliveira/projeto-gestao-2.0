from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    # Criar uma imagem com fundo azul
    img = Image.new('RGB', (size, size), color='#4a47a3')
    draw = ImageDraw.Draw(img)
    
    # Adicionar texto "PG" (Projeto Gestão)
    try:
        # Tentar usar uma fonte do sistema
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback para fonte padrão
        font = ImageFont.load_default()
    
    text = "PG"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Salvar a imagem
    os.makedirs('static/icons', exist_ok=True)
    img.save(f'static/icons/{filename}')

# Criar ícones de diferentes tamanhos
create_icon(192, 'icon-192.png')
create_icon(512, 'icon-512.png')

print("Ícones criados com sucesso!") 