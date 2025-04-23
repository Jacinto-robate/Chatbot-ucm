

# Importando as bibliotecas necessárias
import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import unidecode

# Variável global para o modelo de Sentence Transformer
modelo = None

def carregar_dados(caminho_arquivo):
    """
    Carrega os dados do arquivo de texto para a memória.
    
    Args:
        caminho_arquivo (str): Caminho para o arquivo de dados da faculdade
        
    Returns:
        list: Lista de frases/parágrafos do arquivo
        str: Mensagem de status
    """
    # Verificar se o arquivo existe
    if not os.path.exists(caminho_arquivo):
        return [], "Erro: Arquivo de dados não encontrado!"
    
    try:
        # Abrir e ler o conteúdo do arquivo
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            # Lê o conteúdo completo
            conteudo = arquivo.read()
            
            # Divide o conteúdo por linhas para obter frases distintas
            sentencas = [linha.strip() for linha in conteudo.split('\n') if linha.strip()]
            
            # Carrega o modelo de Sentence Transformers
            global modelo
            try:
                modelo = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                return [], f"Erro ao carregar modelo Sentence Transformers: {e}"
            
            return sentencas, f"Base de conhecimento carregada com sucesso! ({len(sentencas)} itens)"
    except Exception as e:
        return [], f"Erro ao carregar dados: {e}"

def preprocessar_texto(texto):
    """
    Pré-processa o texto para melhorar a precisão da busca.
    
    Args:
        texto (str): Texto a ser pré-processado
        
    Returns:
        str: Texto pré-processado
    """
    # Converter para minúsculas
    texto = texto.lower()
    
    # Remover acentos usando unidecode
    texto = unidecode.unidecode(texto)
    
    # Remover caracteres especiais, mantendo apenas letras, números e espaços
    texto = re.sub(r'[^\w\s]', ' ', texto)
    
    # Remover espaços extras
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def extrair_palavras_chave(texto, min_comprimento=3):
    """
    Extrai palavras-chave relevantes de um texto processado, excluindo stopwords.
    
    Args:
        texto (str): Texto processado para extrair palavras-chave
        min_comprimento (int): Comprimento mínimo para considerar uma palavra
        
    Returns:
        list: Lista de palavras-chave extraídas
    """
    # Palavras para ignorar (stop words em português)
    stop_words = {
        'a', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo', 'as', 'até',
        'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele', 'deles', 'depois',
        'do', 'dos', 'e', 'ela', 'elas', 'ele', 'eles', 'em', 'entre', 'era',
        'eram', 'essa', 'essas', 'esse', 'esses', 'esta', 'estas', 'este', 'estes',
        'eu', 'foi', 'foram', 'há', 'isso', 'isto', 'já', 'lhe', 'lhes',
        'mais', 'mas', 'me', 'mesmo', 'meu', 'meus', 'minha', 'minhas', 'muito',
        'na', 'nas', 'nem', 'no', 'nos', 'nós', 'nossa', 'nossas', 'nosso', 'nossos',
        'num', 'numa', 'o', 'os', 'ou', 'para', 'pela', 'pelas', 'pelo', 'pelos',
        'por', 'qual', 'quando', 'que', 'quem', 'são', 'se', 'seja', 'sejam',
        'sem', 'será', 'seu', 'seus', 'só', 'somos', 'sua', 'suas', 'também',
        'te', 'tem', 'tém', 'têm', 'temos', 'ter', 'seu', 'seus', 'teu', 'teus',
        'tua', 'tuas', 'um', 'uma', 'umas', 'uns', 'você', 'vocês', 'vos', 'vosso', 'vossos',
        # Stopwords específicas para perguntas
        'qual', 'quais', 'quem', 'onde', 'como', 'quando', 'porque', 'por', 'que', 'quantos',
        'quantas', 'quanto', 'quanta', 'é', 'está', 'estão', 'seria', 'seriam', 'tem', 'têm',
        'pode', 'podem', 'deve', 'devem'
    }
    
    # Tokenização simples usando split()
    palavras = texto.split()
    
    # Filtrar palavras relevantes (não stopwords e com tamanho mínimo)
    palavras_relevantes = [palavra for palavra in palavras if 
                          palavra not in stop_words and 
                          len(palavra) >= min_comprimento and
                          palavra.isalpha()]  # Garantir que seja uma palavra e não um número
    
    return palavras_relevantes

def calcular_pontuacao_combinada(similaridade_semantica, 
                               palavras_chave_pergunta, 
                               texto_processado, 
                               peso_semantico=0.7, 
                               peso_palavras=0.3):
    """
    Calcula uma pontuação combinada baseada na similaridade semântica e
    na sobreposição de palavras-chave.
    
    Args:
        similaridade_semantica (float): Valor de similaridade semântica [0-1]
        palavras_chave_pergunta (list): Lista de palavras-chave da pergunta
        texto_processado (str): O texto da base de conhecimento processado
        peso_semantico (float): Peso para a similaridade semântica [0-1]
        peso_palavras (float): Peso para a sobreposição de palavras [0-1]
        
    Returns:
        float: Pontuação combinada
    """
    # Garantir que os pesos somem 1
    soma_pesos = peso_semantico + peso_palavras
    peso_semantico /= soma_pesos
    peso_palavras /= soma_pesos
    
    # Calcular a sobreposição de palavras-chave
    palavras_no_texto = set(texto_processado.split())
    palavras_encontradas = sum(1 for palavra in palavras_chave_pergunta if palavra in palavras_no_texto)
    
    # Calcular a taxa de sobreposição (normalizada)
    if len(palavras_chave_pergunta) > 0:
        taxa_sobreposicao = palavras_encontradas / len(palavras_chave_pergunta)
    else:
        taxa_sobreposicao = 0.0
    
    # Calcular a pontuação combinada
    pontuacao = (similaridade_semantica * peso_semantico) + (taxa_sobreposicao * peso_palavras)
    
    return pontuacao

def avaliar_perguntas_genericas(pergunta_processada):
    """
    Detecta se a pergunta é de caráter genérico ou aberta, requerendo
    possivelmente múltiplos trechos de informação para uma resposta adequada.
    
    Args:
        pergunta_processada (str): Pergunta pré-processada
        
    Returns:
        float: Pontuação adicional para respostas mais abrangentes [0-0.2]
    """
    # Identificadores de perguntas genéricas/abertas
    termos_genericos = ['fale sobre', 'conte sobre', 'descreva', 'explique', 
                         'informacoes sobre', 'o que e', 'quem e', 'me diga']
    
    # Verificar se a pergunta contém algum dos termos genéricos
    for termo in termos_genericos:
        if termo in pergunta_processada:
            return 0.2  # Incentivo para respostas mais completas
    
    return 0.0  # Retorna 0 se não for pergunta genérica

def buscar_resposta(pergunta, base_conhecimento, threshold=0.35):
    """
    Busca uma resposta para a pergunta na base de conhecimento usando uma combinação
    de Sentence Transformers e análise de palavras-chave.
    
    Args:
        pergunta (str): Pergunta do usuário
        base_conhecimento (list): Lista de frases/parágrafos da base de conhecimento
        threshold (float): Valor mínimo de similaridade para considerar uma resposta válida
        
    Returns:
        dict: Dicionário contendo a resposta ou None
    """
    global modelo
    if modelo is None:
        try:
            modelo = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            return {"resposta": None, "erro": f"Erro ao carregar modelo: {e}"}

    # Pré-processar a pergunta
    pergunta_processada = preprocessar_texto(pergunta)
    
    # Extrair palavras-chave da pergunta
    palavras_chave = extrair_palavras_chave(pergunta_processada)
    
    # Verificar se é uma pergunta genérica que pode exigir informações mais abrangentes
    bonus_generica = avaliar_perguntas_genericas(pergunta_processada)
    
    try:
        # Gerar embeddings para a pergunta
        pergunta_embedding = modelo.encode([pergunta], convert_to_tensor=True, show_progress_bar=False)
        
        # Gerar embeddings para os textos da base
        textos_embeddings = modelo.encode(base_conhecimento, convert_to_tensor=True, show_progress_bar=False)
        
        # Calcular a similaridade entre a pergunta e cada frase da base
        similaridades = cosine_similarity(
            pergunta_embedding.cpu().numpy(), 
            textos_embeddings.cpu().numpy()
        )[0]
        
        # Pré-processar todas as frases da base de conhecimento
        textos_processados = [preprocessar_texto(texto) for texto in base_conhecimento]
        
        # Calcular pontuações combinadas (similaridade semântica + palavras-chave)
        pontuacoes = []
        for i, texto_processado in enumerate(textos_processados):
            similaridade = similaridades[i]
            
            # Se for uma pergunta genérica e a similaridade for decente, dar um bônus
            if bonus_generica > 0 and similaridade > threshold:
                similaridade += bonus_generica
            
            # Calcular a pontuação combinada para este texto
            pontuacao = calcular_pontuacao_combinada(
                similaridade, 
                palavras_chave, 
                texto_processado
            )
            
            pontuacoes.append(pontuacao)
        
        # Converter para array numpy para facilitar operações
        pontuacoes = np.array(pontuacoes)
        
        # Verificar se temos pontuações acima do threshold
        if np.max(pontuacoes) >= threshold:
            # Encontrar o índice do texto com a maior pontuação
            indice_melhor_resposta = np.argmax(pontuacoes)
            
            # Para perguntas genéricas com similaridade moderada, combinar múltiplas respostas
            if bonus_generica > 0:
                # Encontrar os N melhores resultados
                indices_melhores = np.argsort(pontuacoes)[-3:]  # Pegar os 3 melhores
                indices_melhores = [i for i in indices_melhores if pontuacoes[i] >= threshold]
                
                if len(indices_melhores) > 1:
                    # Combinar os resultados em uma única resposta
                    resposta_combinada = " ".join([base_conhecimento[i] for i in sorted(indices_melhores)])
                    return {"resposta": resposta_combinada}
            
            # Caso padrão: retornar a melhor resposta singular
            return {"resposta": base_conhecimento[indice_melhor_resposta]}
        else:
            # Nenhuma resposta adequada encontrada
            # Tentar encontrar pelo menos uma resposta parcial com base nas palavras-chave
            contagens_palavras = []
            for texto_processado in textos_processados:
                palavras_texto = set(texto_processado.split())
                contagem = sum(1 for palavra in palavras_chave if palavra in palavras_texto)
                contagens_palavras.append(contagem)
            
            # Se houver pelo menos uma palavra-chave em algum texto
            if max(contagens_palavras) > 0:
                indice_melhor_parcial = np.argmax(contagens_palavras)
                return {"resposta": base_conhecimento[indice_melhor_parcial]}
            
            # Realmente não encontrou nada útil
            return {"resposta": None}
            
    except Exception as e:
        return {"resposta": None, "erro": f"Erro no processamento do texto: {e}"}