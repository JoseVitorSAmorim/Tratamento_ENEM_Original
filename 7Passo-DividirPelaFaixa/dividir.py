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

def encontrar_faixa_divisoria(imagem, cor_alvo, tolerancia=25):
    """
    Identifica as linhas divisórias por densidade horizontal de cor,
    garantindo detecção mesmo com pequenas distorções ou rotações na página.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    linhas_detectadas = []
    
    # Amostragem horizontal (ignora margens extremas para evitar ruídos de borda)
    x_inicio = int(largura * 0.15)
    x_fim = int(largura * 0.85)
    passo_x = 4  # Otimiza a velocidade saltando de 4 em 4 pixels horizontais
    pontos_totais = len(range(x_inicio, x_fim, passo_x))
    
    for y in range(altura):
        pixels_validos = 0
        for x in range(x_inicio, x_fim, passo_x):
            pixel = pixels[x, y]
            r, g, b = pixel[:3]
            
            if (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia):
                pixels_validos += 1
        
        # Se mais de 75% da linha horizontal contiver a cor alvo, é uma divisória
        if (pixels_validos / pontos_totais) > 0.75:
            linhas_detectadas.append(y)
            
    posicoes_corte = []
    if not linhas_detectadas:
        return posicoes_corte
        
    # Agrupa linhas consecutivas (faixas pretas grossas) e captura o pixel inicial de cada uma
    grupo_atual = [linhas_detectadas[0]]
    for y in linhas_detectadas[1:]:
        if y - grupo_atual[-1] <= 15:
            grupo_atual.append(y)
        else:
            posicoes_corte.append(grupo_atual[0])
            grupo_atual = [y]
    if grupo_atual:
        posicoes_corte.append(grupo_atual[0])
        
    # Filtro de proximidade: Impede que ruídos internos criem mini-cortes colados
    posicoes_finais = []
    for p in posicoes_corte:
        if not posicoes_finais or (p - posicoes_finais[-1] >= 150):
            posicoes_finais.append(p)
            
    return posicoes_finais

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem mantendo o fluxo contínuo de pixels sem deixar nenhum 'limbo' invisível
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Busca os topos exatos das faixas pretas horizontais
    posicoes_corte = encontrar_faixa_divisoria(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma linha divisória válida foi encontrada!")
        return
    
    print(f"Total de questões detectadas: {len(posicoes_corte)}")
    
    os.makedirs(pasta_saida, exist_ok=True)
    posicao_anterior = 0
    
    for i, topo_linha in enumerate(posicoes_corte):
        # Define o ponto de corte 8 pixels antes da linha começar para dar respiro visual
        posicao_corte = max(0, topo_linha - 15)
        
        if list(posicoes_corte).count(posicao_corte) > 1 or posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # ESTRATÉGIA CRUCIAL: A próxima questão inicia exatamente onde esta terminou.
        # Zero descarte de dados. A linha preta e o título descem íntegros para o próximo bloco.
        posicao_anterior = posicao_corte
    
    # Salva a última seção restante até o final do documento
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png" 
    pasta_saida = "questoes_completas" 

    # Padrão GIMP fornecido: R=17.3 G=18.0 B=20.8
    cor_do_padrao = converter_cor_gimp_para_rgb(17.3, 18.0, 20.8) 
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Processo concluído com proteção de títulos ativada!")