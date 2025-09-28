"""
Input Text Generation Module

This module handles the generation of Portuguese text content with numbers
for TTS (Text-to-Speech) exercises.
"""

import random
from num2words import num2words

# -------------------------------
# NUMBER TO BRAZILIAN PORTUGUESE
# -------------------------------
def number_to_pt_br(number):
    """
    Convert a number (integer or float) to Brazilian Portuguese words.
    Years will also work.
    
    Args:
        number: The number to convert (int or float)
    
    Returns:
        str: The number written in Brazilian Portuguese words
    """
    return num2words(number, lang='pt_BR')

# -------------------------------
# PARAGRAPH GENERATOR
# -------------------------------
def generate_paragraph():
    """
    Generate a random paragraph with years, large numbers, and percentages
    for listening practice.
    
    Returns:
        str: A paragraph in Brazilian Portuguese with various numbers
    """
    year1 = random.randint(1900, 2025)
    year2 = random.randint(1900, 2025)
    pop1 = random.randint(100000, 5000000)
    pop2 = random.randint(100000, 5000000)
    gdp1 = random.randint(1000000, 50000000)
    gdp2 = random.randint(1000000, 50000000)
    growth = round(random.uniform(1, 20), 1)

    paragraph = (
        f"Em {number_to_pt_br(year1)}, a população da cidade era de {number_to_pt_br(pop1)} habitantes. "
        f"Em {number_to_pt_br(year2)}, esse número aumentou para {number_to_pt_br(pop2)}, "
        f"representando um crescimento de {number_to_pt_br(growth)} por cento. "
        f"O PIB passou de {number_to_pt_br(gdp1)} para {number_to_pt_br(gdp2)} reais."
    )
    return paragraph

def generate_paragraph2():
    text = """
    Verbo: FALAR
    Eu falo muito. Você falou com a professora, e ele falava sobre o tempo. Ela falará a verdade. Nós falamos português, e a gente falou sobre a viagem. Vocês falavam ao telefone, e eles falarão em público. Eu falei com meu amigo, e você falava sempre em voz alta. Ele fala sobre o projeto, e ela falou com a família. Nós falávamos na aula, e a gente falará com o chefe. Eles falam no carro, e elas falaram de mim.
    (pausa)
    Verbo: COMER
    Eu como uma maçã. Você comeu o bolo inteiro, e ele comia arroz e feijão. Ela comerá com pressa. Nós comemos no restaurante, e a gente comeu a lasanha. Vocês comiam a sobremesa, e eles comerão pizza. Eu comi a sopa, e você comia devagar. Ele come um sanduíche, e ela comeu os vegetais. Nós comíamos no café da manhã, e a gente comerá no almoço. Eles comem a carne, e elas comeram o peixe.
    (pausa)
    Verbo: ENTENDER
    Eu entendo a lição. Você entendeu o problema, e ele entendia o que eu dizia. Ela entenderá o recado. Nós entendemos a situação, e a gente entendeu a regra. Vocês entendiam a conversa, e eles entenderão a piada. Eu entendi o filme, e você entendia a sua língua. Ele entende a matemática, e ela entendeu as instruções. Nós entendíamos os nossos amigos, e a gente entenderá a nossa decisão. Eles entendem o manual, e elas entenderam o que aconteceu.
    (pausa)
    Verbo: DECIDIR
    Eu decido ir. Você decidiu a cor da tinta, e ele decidia sozinho. Ela decidirá o destino. Nós decidimos a melhor rota, e a gente decidiu o que fazer. Vocês decidiam o que iam comer, e eles decidirão o futuro do projeto. Eu decidi a compra, e você decidia o preço. Ele decide o filme, e ela decidiu o que queria. Nós decidíamos por conta própria, e a gente decidirá amanhã. Eles decidem o jogo, e elas decidiram a viagem.
    (pausa)
    Verbo: VIVER
    Eu vivo em São Paulo. Você viveu em Minas Gerais, e ele vivia com os avós. Ela viverá no exterior. Nós vivemos bem, e a gente viveu um momento difícil. Vocês viviam na cidade, e eles viverão a vida em paz. Eu vivi na praia, e você vivia no campo. Ele vive o momento, e ela viveu a experiência. Nós vivíamos em uma casa grande, e a gente viverá juntos. Eles vivem no mesmo prédio, e elas viveram a vida com alegria.
    """
    return text

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------
def generate_and_display_paragraph():
    """
    Generate a paragraph and display it.
    
    Returns:
        str: Generated paragraph text
    """
    paragraph = generate_paragraph()
    print("Generated paragraph:")
    print(paragraph)
    print()  # Add spacing
    return paragraph
