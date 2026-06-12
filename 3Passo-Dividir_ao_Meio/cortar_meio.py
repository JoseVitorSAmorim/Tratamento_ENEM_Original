from PIL import Image
import os

pasta_imagens = "sem-bordas-externas"
pasta_saida = "divididas-com-bordas-do-meio"

os.makedirs(pasta_saida, exist_ok=True)

for nome_arquivo in os.listdir(pasta_imagens):
    if nome_arquivo.lower().endswith('.png'):
        caminho_entrada = os.path.join(pasta_imagens, nome_arquivo)
        imagem = Image.open(caminho_entrada)

        largura, altura = imagem.size
        
        metade_largura = largura // 2
        
        caixa_esquerda = (0, 0, metade_largura, altura)
        imagem_esquerda = imagem.crop(caixa_esquerda)
        
        caixa_direita = (metade_largura, 0, largura, altura)
        imagem_direita = imagem.crop(caixa_direita)
        
        nome_base, extensao = os.path.splitext(nome_arquivo)
        
        caminho_esquerda = os.path.join(pasta_saida, f"{nome_base}_esquerda{extensao}")
        caminho_direita = os.path.join(pasta_saida, f"{nome_base}_direita{extensao}")
        
        imagem_esquerda.save(caminho_esquerda)
        imagem_direita.save(caminho_direita)

print("Divisão das imagens ao meio concluída.")