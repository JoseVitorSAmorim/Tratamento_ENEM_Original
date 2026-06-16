from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_divisoria(imagem, cor_alvo, tolerancia=15, altura_faixa=10):
    """
    Encontra posições onde há uma faixa horizontal da cor especificada
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura - altura_faixa:
        # Verifica se há uma faixa de 'altura_faixa' pixels da cor alvo
        faixa_encontrada = True
        
        for dy in range(altura_faixa):
            # Pega a cor do pixel atual (no canto da imagem para evitar o conteúdo)
            pixel = pixels[largura-2, y + dy]
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se a cor está dentro da tolerância
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            # Corta ANTES da faixa (no pixel anterior)
            posicao_corte = y - 13
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Faixa divisória encontrada em y={y}, cortando em y={posicao_corte}")
            # Pula a faixa inteira para evitar detecções múltiplas
            y += altura_faixa
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando ANTES das faixas divisorias
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições das faixas baseadas na cor alvo
    posicoes_corte = encontrar_faixa_divisoria(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma faixa divisória encontrada na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte + 10  # Pula a faixa de 10 pixels
    
    # Corta a seção final
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo seu caminho
    pasta_saida = "questoes_colunas" 

    # Alterado para o padrão GIMP (0 a 100) solicitado:
    cor_do_padrao = converter_cor_gimp_para_rgb(17.3, 18.0, 20.8) 
    print(f"Cor convertida do GIMP para RGB: {cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")