from PIL import Image
import os

def cor_parecida(pixel, cor_alvo, tolerancia=15):
    """
    Verifica se a cor do pixel está dentro da tolerância da cor alvo.
    Lida com pixels RGB ou RGBA.
    """
    if len(pixel) == 4:
        r, g, b, a = pixel
    else:
        r, g, b = pixel[:3]
        
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_padrao_questoes(imagem, tolerancia_cor=15, offset_x=15):
    """
    Encontra posições baseadas no padrão sequencial de 3 faixas (6px ± 5px, 5px ± 5px, 2px ± 5px).
    'offset_x' define a distância da borda direita para desviar de linhas de margem.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    posicoes_corte = []
    
    # Cores do padrão (Micro-código de barras do ENEM)
    cor_escura = (44, 46, 53)
    cor_branca = (255, 255, 255)
    
    # Define a coluna exata de pixels que será analisada de cima a baixo
    x_alvo = largura - offset_x
    
    y = 0
    # Vai até altura - 30 para evitar estouro de índice no pior cenário do padrão
    while y < altura - 30:
        pixel_atual = pixels[x_alvo, y]
        
        # 1. Tenta achar o início da PRIMEIRA FAIXA (cor escura)
        if cor_parecida(pixel_atual, cor_escura, tolerancia_cor):
            tamanho_f1 = 0
            
            # Conta pixels escuros seguidos
            while y + tamanho_f1 < altura and cor_parecida(pixels[x_alvo, y + tamanho_f1], cor_escura, tolerancia_cor):
                tamanho_f1 += 1
                
            # Margem de erro: 6px ± 5px (entre 1 e 11)
            if 1 <= tamanho_f1 <= 11:
                
                # 2. Inicia contagem da SEGUNDA FAIXA (cor branca)
                y2 = y + tamanho_f1
                tamanho_f2 = 0
                while y2 + tamanho_f2 < altura and cor_parecida(pixels[x_alvo, y2 + tamanho_f2], cor_branca, tolerancia_cor):
                    tamanho_f2 += 1
                    
                # Margem de erro: 5px ± 5px (entre 1 e 10)
                if 1 <= tamanho_f2 <= 10:
                    
                    # 3. Inicia contagem da TERCEIRA FAIXA (cor escura)
                    y3 = y2 + tamanho_f2
                    tamanho_f3 = 0
                    while y3 + tamanho_f3 < altura and cor_parecida(pixels[x_alvo, y3 + tamanho_f3], cor_escura, tolerancia_cor):
                        tamanho_f3 += 1
                        
                    # Margem de erro: 2px ± 5px (entre 1 e 7)
                    if 1 <= tamanho_f3 <= 7:
                        
                        # PADRÃO COMPLETO ENCONTRADO!
                        posicao_corte = y - 13
                        if posicao_corte < 0:
                            posicao_corte = 0
                            
                        posicoes_corte.append(posicao_corte)
                        print(f"Padrão detectado em x={x_alvo}, y={y}. Cortando em y={posicao_corte}")
                        
                        # Pula o bloco inteiro detectado para evitar leituras repetidas
                        y += (tamanho_f1 + tamanho_f2 + tamanho_f3)
                        continue 
                        
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_padrao(caminho_imagem, pasta_saida, offset_x=15):
    """
    Divide a imagem verticalmente cortando ANTES dos padrões detectados.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    print(f"Imagem carregada: {largura}x{altura} pixels (Análise em offset_x={offset_x})")
    
    posicoes_corte = encontrar_padrao_questoes(imagem, offset_x=offset_x)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem! Verifique o valor de offset_x.")
        return
        
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    
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
        
        # Faz a próxima questão começar exatamente onde o topo do cabeçalho da questão foi cortado
        posicao_anterior = posicao_corte + 13
        
    # Corta a última seção restante da imagem
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    # --- CONFIGURAÇÃO PARA COLUNAS CONCATENADAS ---
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_colunas"
    offset_ajustado = 15  # 15px funciona bem tanto para colunas limpas quanto com bordas
    
    # --- CONFIGURAÇÃO PARA PÁGINAS INTEIRAS (Descomente para usar) ---
    # caminho_imagem = "./inteiras/pagina_enem_3_direita.jpg"
    # pasta_saida = "pagina_3_direita"
    # offset_ajustado = 15  # Move a varredura para dentro, ignorando a linha preta da margem externa
    
    # Executa o processo
    dividir_imagem_por_padrao(caminho_imagem, pasta_saida, offset_x=offset_ajustado)
    print("Divisão concluída!")