from PIL import Image
import os

pasta_imagens = "imagens-convertidas"
pasta_saida = "sem-bordas-externas"

os.makedirs(pasta_saida, exist_ok=True)

for nome_arquivo in os.listdir(pasta_imagens):
    if nome_arquivo.lower().endswith(".png"):
        caminho_entrada = os.path.join(pasta_imagens, nome_arquivo)
        imagem = Image.open(caminho_entrada)

        largura, altura = imagem.size

        # Definição de corte proporcional
        esquerda = int(largura * 0.04)   # Mantém 96% da imagem a partir da esquerda
        topo = int(altura * 0.065)       # Remove o topo (logo/barcode)
        direita = int(largura * 0.965)   # Remove a margem branca fina da direita
        base = int(altura * 0.96)        # Remove o rodapé com o número da página

        caixa_corte = (esquerda, topo, direita, base)
        imagem_cortada = imagem.crop(caixa_corte)

        caminho_saida = os.path.join(pasta_saida, nome_arquivo)
        imagem_cortada.save(caminho_saida)

print("Recorte das bordas concluído.")