from PIL import Image, ImageDraw, ImageFont, ImageFilter

def criar_proposta(dados):
    W, H = 1080, 1350

    # --- FUNDO ---
    try:
        bg = Image.open("fundo.png").convert("RGBA")
        bg = bg.resize((W, H), Image.LANCZOS)
        img = bg.copy()
    except:
        img = Image.new("RGBA", (W, H), (255, 255, 255, 255))

    base_draw = ImageDraw.Draw(img)

    # --- CORES ---
    LARANJA     = (243, 112, 33, 255)
    AZUL_LEGACY = (0, 35, 95, 255)
    PRETO       = (15, 15, 15, 255)
    CINZA_TEXTO = (90, 90, 90, 255)

    # Esquelmorfo
    PAINEL_FILL   = (255, 255, 255, 210)   # translúcido
    PAINEL_BORDA  = (220, 220, 220, 255)
    PAINEL_BRILHO = (255, 255, 255, 120)

    VERDE_BADGE = (40, 170, 90, 255)
    VERM_BADGE  = (220, 60, 60, 255)
    CINZA_BADGE = (40, 40, 40, 255)

    # --- FONTES ---
    try:
        f_titulo      = ImageFont.truetype("bold.ttf", 46)   # FIPE
        f_subtitulo   = ImageFont.truetype("bold.ttf", 34)   # Modelo
        f_texto       = ImageFont.truetype("regular.ttf", 28)
        f_negrito     = ImageFont.truetype("bold.ttf", 28)
        f_head_planos = ImageFont.truetype("bold.ttf", 26)
        f_preco_num   = ImageFont.truetype("bold.ttf", 34)
        f_preco_rs    = ImageFont.truetype("regular.ttf", 22)
        f_small       = ImageFont.truetype("regular.ttf", 22)
        f_footer      = ImageFont.truetype("bold.ttf", 22)
    except:
        f_titulo = f_subtitulo = f_texto = f_negrito = f_head_planos = f_preco_num = f_preco_rs = f_small = f_footer = ImageFont.load_default()

    MARGEM_X = 70
    CENTRO_X = W // 2

    # =========================================================
    # 1) TOPO FIXO (não precisa mexer muito)
    # =========================================================
    y = 175
    base_draw.text((MARGEM_X, y), "Proposta para:", font=f_texto, fill=CINZA_TEXTO)
    base_draw.text((MARGEM_X + 215, y), dados["cliente"], font=f_negrito, fill=AZUL_LEGACY)
    y += 42

    base_draw.text((MARGEM_X, y), f"Consultor(a): {dados['consultor']}", font=f_negrito, fill=LARANJA)
    y += 55

    base_draw.line([(MARGEM_X, y), (W - MARGEM_X, y)], fill=(210, 210, 210, 255), width=2)
    y += 35

    base_draw.text((CENTRO_X, y), dados["modelo"], font=f_subtitulo, fill=PRETO, anchor="ma")
    y += 46

    base_draw.text((CENTRO_X, y), f"Ano: {dados['ano']}  |  FIPE: {dados['fipe']}",
                   font=f_titulo, fill=AZUL_LEGACY, anchor="ma")
    y += 70

    # badge adesão
    badge_w, badge_h = 520, 64
    bx0 = CENTRO_X - badge_w // 2
    by0 = y
    base_draw.rounded_rectangle([bx0, by0, bx0 + badge_w, by0 + badge_h], radius=16, fill=(245, 245, 245, 235))
    base_draw.text((CENTRO_X, by0 + 20), f"Adesão: R$ {dados['adesao']}", font=f_subtitulo, fill=PRETO, anchor="ma")

    # =========================================================
    # 2) PAINEL ESQUELMORFO (cobre veículos se precisar)
    # =========================================================
    # Você liberou usar a área dos veículos. Então o painel começa alto o suficiente pra caber tudo.
    painel_x0, painel_x1 = 55, W - 55
    painel_y0, painel_y1 = 650, H - 40  # COMEÇA MAIS CEDO PRA CABER A LISTA INTEIRA
    painel_w = painel_x1 - painel_x0
    painel_h = painel_y1 - painel_y0

    # sombra (layer separado)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([painel_x0+6, painel_y0+10, painel_x1+6, painel_y1+10],
                         radius=28, fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, shadow)

    # painel
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([painel_x0, painel_y0, painel_x1, painel_y1], radius=28,
                         fill=PAINEL_FILL, outline=PAINEL_BORDA, width=2)
    # brilho no topo (efeito “plástico”)
    pd.rounded_rectangle([painel_x0+2, painel_y0+2, painel_x1-2, painel_y0 + int(painel_h*0.22)],
                         radius=26, fill=PAINEL_BRILHO)

    img = Image.alpha_composite(img, panel)
    draw = ImageDraw.Draw(img)

    # =========================================================
    # 3) GRID DE PLANOS + BENEFÍCIOS COM ALTURA DINÂMICA
    # =========================================================
    itens = [
        ("Rastreamento", ["✔", "✔", "✔", "✔"]),
        ("Reboque",      ["200", "400", "1mil", "1mil"]),
        ("Roubo/Furto",  ["✖", "✔", "✔", "✔"]),
        ("Colisão/PT",   ["✖", "✖", "✔", "✔"]),
        ("Terceiros",    ["✖", "✖", "✔", "✔"]),
        ("Vidros",       ["✖", "✖", "✔", "✔"]),
        ("Carro Res.",   ["✖", "✖", "10d", "30d"]),
        ("Gás (GNV)",    ["✖", "✖", "✖", "✔"]),
    ]

    # Área interna do painel
    pad = 28
    inner_x0 = painel_x0 + pad
    inner_x1 = painel_x1 - pad
    inner_y0 = painel_y0 + 20
    inner_y1 = painel_y1 - 18
    inner_w = inner_x1 - inner_x0
    inner_h = inner_y1 - inner_y0

    # Reserva de alturas fixas (títulos + preços + divisores + rodapé)
    head_h   = 40     # títulos Econ/Básico/Plus/Prem
    line_h   = 18     # linha
    preco_h  = 78     # R$ + número
    gap1     = 18
    footer_h = 72     # promo + legal (2 linhas)
    gap2     = 12

    # Espaço restante para lista de itens
    lista_h = inner_h - (head_h + line_h + preco_h + gap1 + footer_h + gap2)
    # row height calculado (garante caber tudo)
    row_h = max(42, int(lista_h / len(itens)))  # mínimo 42 pra não ficar miúdo

    # Colunas: 1 label + 4 planos
    label_w = 310
    col_w = (inner_w - label_w) / 4
    x_label = inner_x0 + 8
    x_cols = [inner_x0 + label_w + (i * col_w) + (col_w / 2) for i in range(4)]

    # --- Cabeçalho colunas ---
    y0 = inner_y0
    colunas = ["Econ.", "Básico", "Plus", "Prem."]
    for i, col in enumerate(colunas):
        draw.text((x_cols[i], y0 + 12), col, font=f_head_planos, fill=LARANJA, anchor="mm")

    # Linha preta
    y_line = y0 + head_h
    draw.line([(inner_x0, y_line), (inner_x1, y_line)], fill=PRETO, width=3)

    # --- Preços ---
    y_preco = y_line + 18
    for i, p in enumerate(dados["precos"]):
        valor = p.replace("R$ ", "")
        draw.text((x_cols[i], y_preco + 10), "R$", font=f_preco_rs, fill=PRETO, anchor="mm")
        draw.text((x_cols[i], y_preco + 44), valor, font=f_preco_num, fill=PRETO, anchor="mm")

    # divisor sutil abaixo dos preços
    y_div = y_preco + preco_h
    draw.line([(inner_x0, y_div), (inner_x1, y_div)], fill=(210, 210, 210, 255), width=2)

    # --- Ícones bonitos (badge circular) ---
    def draw_badge(x, y, kind):
        r = 14
        if kind == "check":
            draw.ellipse([x-r, y-r, x+r, y+r], fill=VERDE_BADGE)
            # check branco “desenhado”
            draw.line([(x-6, y+1), (x-1, y+6)], fill=(255,255,255,255), width=3)
            draw.line([(x-1, y+6), (x+8, y-5)], fill=(255,255,255,255), width=3)
        elif kind == "x":
            draw.ellipse([x-r, y-r, x+r, y+r], fill=VERM_BADGE)
            draw.line([(x-6, y-6), (x+6, y+6)], fill=(255,255,255,255), width=3)
            draw.line([(x+6, y-6), (x-6, y+6)], fill=(255,255,255,255), width=3)

    def draw_pill(x, y, txt):
        # pill para "200", "10d", "1mil"
        tw, th = draw.textbbox((0,0), txt, font=f_negrito)[2:]
        pw = max(54, tw + 26)
        ph = 32
        px0, py0 = x - pw/2, y - ph/2
        draw.rounded_rectangle([px0, py0, px0+pw, py0+ph], radius=14, fill=(245,245,245,255), outline=(215,215,215,255), width=2)
        draw.text((x, y-1), txt, font=f_negrito, fill=PRETO, anchor="mm")

    # --- Lista de benefícios ---
    y_list = y_div + gap1
    for nome, status_lista in itens:
        y_mid = y_list + (row_h // 2)

        draw.text((x_label, y_mid), nome, font=f_texto, fill=CINZA_TEXTO, anchor="lm")

        for i, st in enumerate(status_lista):
            cx = x_cols[i]
            if st == "✔":
                draw_badge(cx, y_mid, "check")
            elif st == "✖":
                draw_badge(cx, y_mid, "x")
            else:
                draw_pill(cx, y_mid, st)

        y_list += row_h

    # --- Rodapé dentro do painel (sempre visível) ---
    y_footer = inner_y1 - footer_h + 10
    draw.text((CENTRO_X, y_footer + 10), "⚠ PAGAMENTO ANTECIPADO GERA DESCONTO ⚠",
              font=f_footer, fill=LARANJA, anchor="mm")
    draw.text((CENTRO_X, y_footer + 42), "A COTAÇÃO PODE SOFRER ALTERAÇÕES BASEADAS NOS VALORES VIGENTES",
              font=f_small, fill=AZUL_LEGACY, anchor="mm")

    return img.convert("RGB")
