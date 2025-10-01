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

def format_number_br(number):
    """
    Format a number using Brazilian digit conventions.
    - Thousands separator: . (dot)
    - Decimal separator: , (comma)
    
    Args:
        number: The number to format (int or float)
    
    Returns:
        str: The number formatted in Brazilian style
    
    Examples:
        3416 -> "3.416"
        50000 -> "50.000"
        3.5 -> "3,5"
        185.1 -> "185,1"
    """
    if isinstance(number, float):
        # Format with one decimal place
        formatted = f"{number:,.1f}"
        # Replace: comma->X, dot->comma, X->dot (to swap separators)
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
    else:
        # Format integer with thousand separators
        formatted = f"{number:,}"
        # Replace comma with dot for Brazilian format
        return formatted.replace(',', '.')

# -------------------------------
# PARAGRAPH GENERATOR
# -------------------------------
def generate_paragraph(use_digits=True):
    """
    Generate a random paragraph with years, large numbers, and percentages
    for listening practice. Creates a fictional history narrative spanning 
    from 1400 to 2025 with extensive use of years and various numbers.
    
    Args:
        use_digits: If True, format numbers as digits (e.g., "1.417"). 
                   If False, format as Portuguese words (e.g., "mil, quatrocentos e dezessete")
    
    Returns:
        str: A paragraph in Brazilian Portuguese with various numbers
    """
    # Generate 20+ unique years between 1400 and 2025
    years = random.sample(range(1400, 2026), 25)
    years.sort()
    
    # Generate various numbers for the narrative
    founding_pop = random.randint(3000, 8000)
    first_army = random.randint(500, 1500)
    distance1 = random.randint(150, 450)
    treasure1 = random.randint(50000, 150000)
    expansion_area = random.randint(12000, 35000)
    treaty_articles = random.randint(15, 45)
    fleet_ships = random.randint(75, 200)
    university_students = random.randint(800, 2500)
    war_casualties = random.randint(15000, 75000)
    alliance_nations = random.randint(7, 18)
    population_growth = round(random.uniform(150, 380), 1)
    trade_routes = random.randint(28, 67)
    palace_rooms = random.randint(350, 850)
    library_volumes = random.randint(45000, 125000)
    rebellion_participants = random.randint(8000, 25000)
    reform_percentage = round(random.uniform(35, 85), 1)
    industrial_factories = random.randint(125, 450)
    railroad_km = random.randint(2500, 7800)
    modern_population = random.randint(1500000, 8500000)
    gdp_billions = round(random.uniform(125, 550), 1)
    tech_companies = random.randint(1250, 4800)
    unemployment_rate = round(random.uniform(3.2, 8.7), 1)
    
    # Choose formatting function based on use_digits
    fmt = format_number_br if use_digits else number_to_pt_br
    
    paragraph = (
        f"A história do lendário Império de Valória começa em {fmt(years[0])}, quando o rei fundador estabeleceu "
        f"a primeira capital com apenas {fmt(founding_pop)} habitantes e um exército de {fmt(first_army)} soldados. "
        f"Em {fmt(years[1])}, exploradores valorenses descobriram terras a {fmt(distance1)} quilômetros ao norte, "
        f"onde encontraram um tesouro avaliado em {fmt(treasure1)} moedas de ouro. "
        f"O império expandiu significativamente em {fmt(years[2])}, conquistando {fmt(expansion_area)} quilômetros quadrados de território. "
        f"Em {fmt(years[3])}, foi assinado o Tratado de Paz com {fmt(treaty_articles)} artigos. "
        f"A frota naval, construída em {fmt(years[4])}, possuía {fmt(fleet_ships)} navios de guerra. "
        f"A primeira universidade, fundada em {fmt(years[5])}, recebia {fmt(university_students)} estudantes anualmente. "
        f"A Grande Guerra de {fmt(years[6])} resultou em {fmt(war_casualties)} baixas. "
        f"Em {fmt(years[7])}, formou-se uma aliança com {fmt(alliance_nations)} nações vizinhas. "
        f"Durante o século seguinte, entre {fmt(years[8])} e {fmt(years[9])}, a população cresceu {fmt(population_growth)} por cento. "
        f"Em {fmt(years[10])}, estabeleceram-se {fmt(trade_routes)} rotas comerciais marítimas. "
        f"O palácio real, concluído em {fmt(years[11])}, tinha {fmt(palace_rooms)} aposentos luxuosos. "
        f"A Grande Biblioteca, inaugurada em {fmt(years[12])}, armazenava {fmt(library_volumes)} volumes raros. "
        f"Uma rebelião em {fmt(years[13])} mobilizou {fmt(rebellion_participants)} cidadãos descontentes. "
        f"As reformas políticas de {fmt(years[14])} mudaram {fmt(reform_percentage)} por cento das leis antigas. "
        f"A Revolução Industrial chegou em {fmt(years[15])}, trazendo {fmt(industrial_factories)} fábricas. "
        f"Em {fmt(years[16])}, construíram {fmt(railroad_km)} quilômetros de ferrovias. "
        f"Durante {fmt(years[17])} e {fmt(years[18])}, o império se modernizou rapidamente. "
        f"Em {fmt(years[19])}, a população atingiu {fmt(modern_population)} habitantes. "
        f"O PIB em {fmt(years[20])} alcançou {fmt(gdp_billions)} bilhões. "
        f"Em {fmt(years[21])}, surgiram {fmt(tech_companies)} empresas de tecnologia. "
        f"Entre {fmt(years[22])} e {fmt(years[23])}, houve grande prosperidade econômica. "
        f"Finalmente, em {fmt(years[24])}, o império moderno mantém uma taxa de desemprego de apenas {fmt(unemployment_rate)} por cento."
    )
    return paragraph

def generate_paragraph_num1():
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
def generate_and_display_paragraph(use_digits=True):
    """
    Generate a paragraph and display it.
    
    Args:
        use_digits: If True, format numbers as digits. If False, format as Portuguese words
    
    Returns:
        str: Generated paragraph text
    """
    paragraph = generate_paragraph(use_digits=use_digits)
    print("Generated paragraph:")
    print(paragraph)
    print()  # Add spacing
    return paragraph
