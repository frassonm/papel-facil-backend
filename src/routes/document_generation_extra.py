from flask import Blueprint, request, send_file
from fpdf import FPDF
import io
from datetime import datetime
import re

# Importar constantes de poderes e função auxiliar
from .document_generation import PODERES_PROCURACAO, PODERES_REPRESENTACAO, PODERES_SUBSTABELECIMENTO, remover_cep

extra_bp = Blueprint('document_generation_extra', __name__)

# ============================================================================
# PROCURAÇÃO PJ COM MÚLTIPLOS OUTORGADOS
# ============================================================================

@extra_bp.route('/generate_procuracao_pj_multiplos', methods=['POST'])
def generate_procuracao_pj_multiplos():
    """
    Gera uma procuração para Pessoa Jurídica com Múltiplos Outorgados em formato PDF
    OTIMIZADO PARA CABER EM 1 PÁGINA - TEXTO JUSTIFICADO
    """
    data = request.get_json()
    
    # Extrair dados do OUTORGANTE (Pessoa Jurídica)
    outorgante_razao_social = data.get("outorganteRazaoSocial", "")
    outorgante_cnpj = data.get("outorganteCnpj", "")
    outorgante_endereco = remover_cep(data.get("outorganteEndereco", ""))
    
    # Extrair lista de OUTORGADOS (array de objetos)
    outorgados = data.get("outorgados", [])
    
    # Extrair dados do VEÍCULO
    veiculo_nome = data.get("veiculoNome", "")
    veiculo_placa = data.get("veiculoPlaca", "")
    veiculo_renavam = data.get("veiculoRenavam", "")
    veiculo_chassi = data.get("veiculoChassi", "")
    veiculo_ano_modelo = data.get("veiculoAnoModelo", "")
    veiculo_cor = data.get("veiculoCor", "")
    
    local_emissao = data.get("localEmissao", "")
    data_emissao = data.get("dataEmissao", "")
    
    # Converter data
    if data_emissao:
        try:
            data_obj = datetime.strptime(data_emissao, "%Y-%m-%d")
            data_emissao = data_obj.strftime("%d/%m/%Y")
        except ValueError:
            pass
    
    poderes = data.get("poderes", PODERES_PROCURACAO)

    # Criar PDF - ESPAÇAMENTOS REDUZIDOS MAS EQUILIBRADOS
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    # Título
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 8, "PROCURAÇÃO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # OUTORGANTE (PJ) - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGANTE: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{outorgante_razao_social}, inscrito sob o CNPJ: {outorgante_cnpj}, estabelecida em {outorgante_endereco}.")
    pdf.ln(5)

    # NOMEIO E CONSTITUO
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 5, "NOMEIO E CONSTITUO MEU BASTANTE PROCURADOR", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGADOS (Múltiplos) - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGADOS: ")
    pdf.set_font("Times", "", 12)
    
    outorgados_texto = ""
    for i, outorgado in enumerate(outorgados):
        nome = outorgado.get("nome", "")
        nacionalidade = outorgado.get("nacionalidade", "")
        cpf = outorgado.get("cpf", "")
        endereco = remover_cep(outorgado.get("endereco", ""))
        
        if i == len(outorgados) - 1:
            outorgados_texto += f"{nome}, {nacionalidade}, maior, inscrito sob o CPF: {cpf}, residente e domiciliado em {endereco}."
        else:
            outorgados_texto += f"{nome}, {nacionalidade}, maior, inscrito sob o CPF: {cpf}, residente e domiciliado em {endereco}, e/ou: "
    
    pdf.write(5, outorgados_texto)
    pdf.ln(5)

    # REPRESENTAÇÃO - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "REPRESENTAÇÃO: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"para fim especial, podendo vender para si e/ou para terceiros um {veiculo_nome}, Placa: {veiculo_placa}, RENAVAM: {veiculo_renavam}, CHASSI: {veiculo_chassi}, ANO/MODELO {veiculo_ano_modelo}, cor {veiculo_cor}.")
    pdf.ln(5)

    # PODERES - JUSTIFICADO
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, poderes, align="J")
    pdf.ln(5)

    # LOCAL E DATA - JUSTIFICADO
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, f"{local_emissao}, {data_emissao}.", align="J")
    pdf.ln(10)  # Espaço maior para assinatura

    # Assinatura
    pdf.set_line_width(0.5)
    x_start = 60
    x_end = 150
    y_line = pdf.get_y()
    pdf.line(x_start, y_line, x_end, y_line)
    pdf.ln(2)
    pdf.set_font("Times", "", 10)
    pdf.cell(0, 5, "OUTORGANTE", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf_output = pdf.output(dest="S")
    return send_file(
        io.BytesIO(pdf_output),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="procuracao_pj_multiplos.pdf"
    )


# ============================================================================
# PROCURAÇÃO REPRESENTAÇÃO NA COMPRA - PF
# ============================================================================

@extra_bp.route('/generate_representacao_pf', methods=['POST'])
def generate_representacao_pf():
    """
    Gera uma procuração de representação na compra para Pessoa Física em formato PDF
    """
    data = request.get_json()
    
    # Dados do OUTORGANTE (PF)
    outorgante_nome = data.get("outorganteNome", "")
    outorgante_nacionalidade = data.get("outorganteNacionalidade", "")
    outorgante_cpf = data.get("outorganteCpf", "")
    outorgante_endereco = remover_cep(data.get("outorganteEndereco", ""))
    
    # Dados do OUTORGADO (PF)
    outorgado_nome = data.get("outorgadoNome", "")
    outorgado_nacionalidade = data.get("outorgadoNacionalidade", "")
    outorgado_cpf = data.get("outorgadoCpf", "")
    outorgado_endereco = remover_cep(data.get("outorgadoEndereco", ""))
    
    # Dados do VEÍCULO
    veiculo_nome = data.get("veiculoNome", "")
    veiculo_placa = data.get("veiculoPlaca", "")
    veiculo_renavam = data.get("veiculoRenavam", "")
    veiculo_chassi = data.get("veiculoChassi", "")
    veiculo_ano_modelo = data.get("veiculoAnoModelo", "")
    veiculo_cor = data.get("veiculoCor", "")
    
    local_emissao = data.get("localEmissao", "")
    data_emissao = data.get("dataEmissao", "")
    
    # Converter data
    if data_emissao:
        try:
            data_obj = datetime.strptime(data_emissao, "%Y-%m-%d")
            data_emissao = data_obj.strftime("%d/%m/%Y")
        except ValueError:
            pass
    
    # Poderes customizáveis
    poderes = data.get("poderes", PODERES_REPRESENTACAO)
    
    # Criar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    # Título
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "PROCURAÇÃO REPRESENTAÇÃO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGANTE - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGANTE: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{outorgante_nome}, {outorgante_nacionalidade}, maior, inscrito sob o CPF: {outorgante_cpf}, residente e domiciliado em {outorgante_endereco}.")
    pdf.ln(8)

    # NOMEIO E CONSTITUO
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 5, "NOMEIO E CONSTITUO MEU BASTANTE PROCURADOR", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGADOS - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGADOS: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{outorgado_nome}, {outorgado_nacionalidade}, maior, inscrito sob o CPF: {outorgado_cpf}, residente e domiciliado em {outorgado_endereco}.")
    pdf.ln(8)

    # REPRESENTAÇÃO - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "REPRESENTAÇÃO: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{poderes}, do veículo: {veiculo_nome}, Placa: {veiculo_placa}, RENAVAM: {veiculo_renavam}, CHASSI: {veiculo_chassi}, ANO/MODELO {veiculo_ano_modelo}, cor {veiculo_cor}.")
    pdf.ln(8)

    # LOCAL E DATA - JUSTIFICADO
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, f"{local_emissao}, {data_emissao}.", align="J")
    pdf.ln(15)  # Espaço maior para assinatura

    # Assinatura
    pdf.set_line_width(0.5)
    x_start = 60
    x_end = 150
    y_line = pdf.get_y()
    pdf.line(x_start, y_line, x_end, y_line)
    pdf.ln(2)
    pdf.set_font("Times", "", 10)
    pdf.cell(0, 5, "OUTORGANTE", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf_output = pdf.output(dest="S")
    return send_file(
        io.BytesIO(pdf_output),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="representacao_pf.pdf"
    )


# ============================================================================
# PROCURAÇÃO REPRESENTAÇÃO NA COMPRA - PJ
# ============================================================================

@extra_bp.route('/generate_representacao_pj', methods=['POST'])
def generate_representacao_pj():
    """
    Gera uma procuração de representação na compra para Pessoa Jurídica em formato PDF
    """
    data = request.get_json()
    
    # Dados do OUTORGANTE (PJ)
    outorgante_razao_social = data.get("outorganteRazaoSocial", "")
    outorgante_cnpj = data.get("outorganteCnpj", "")
    outorgante_endereco = remover_cep(data.get("outorganteEndereco", ""))
    
    # Dados do OUTORGADO (PF)
    outorgado_nome = data.get("outorgadoNome", "")
    outorgado_nacionalidade = data.get("outorgadoNacionalidade", "")
    outorgado_cpf = data.get("outorgadoCpf", "")
    outorgado_endereco = remover_cep(data.get("outorgadoEndereco", ""))
    
    # Dados do VEÍCULO
    veiculo_nome = data.get("veiculoNome", "")
    veiculo_placa = data.get("veiculoPlaca", "")
    veiculo_renavam = data.get("veiculoRenavam", "")
    veiculo_chassi = data.get("veiculoChassi", "")
    veiculo_ano_modelo = data.get("veiculoAnoModelo", "")
    veiculo_cor = data.get("veiculoCor", "")
    
    local_emissao = data.get("localEmissao", "")
    data_emissao = data.get("dataEmissao", "")
    
    # Converter data
    if data_emissao:
        try:
            data_obj = datetime.strptime(data_emissao, "%Y-%m-%d")
            data_emissao = data_obj.strftime("%d/%m/%Y")
        except ValueError:
            pass
    
    # Poderes customizáveis
    poderes = data.get("poderes", PODERES_REPRESENTACAO)
    
    # Criar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    # Título
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "PROCURAÇÃO REPRESENTAÇÃO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGANTE (PJ) - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGANTE: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{outorgante_razao_social}, inscrito sob o CNPJ: {outorgante_cnpj}, estabelecida em {outorgante_endereco}.")
    pdf.ln(8)

    # NOMEIO E CONSTITUO
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 5, "NOMEIO E CONSTITUO MEU BASTANTE PROCURADOR", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGADOS - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGADOS: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{outorgado_nome}, {outorgado_nacionalidade}, maior, inscrito sob o CPF: {outorgado_cpf}, residente e domiciliado em {outorgado_endereco}.")
    pdf.ln(8)

    # REPRESENTAÇÃO - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "REPRESENTAÇÃO: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{poderes}, do veículo: {veiculo_nome}, Placa: {veiculo_placa}, RENAVAM: {veiculo_renavam}, CHASSI: {veiculo_chassi}, ANO/MODELO {veiculo_ano_modelo}, cor {veiculo_cor}.")
    pdf.ln(8)

    # LOCAL E DATA - JUSTIFICADO
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, f"{local_emissao}, {data_emissao}.", align="J")
    pdf.ln(15)  # Espaço maior para assinatura

    # Assinatura
    pdf.set_line_width(0.5)
    x_start = 60
    x_end = 150
    y_line = pdf.get_y()
    pdf.line(x_start, y_line, x_end, y_line)
    pdf.ln(2)
    pdf.set_font("Times", "", 10)
    pdf.cell(0, 5, "OUTORGANTE", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf_output = pdf.output(dest="S")
    return send_file(
        io.BytesIO(pdf_output),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="representacao_pj.pdf"
    )


# ============================================================================
# SUBSTABELECIMENTO - PF
# ============================================================================

@extra_bp.route('/generate_substabelecimento_pf', methods=['POST'])
def generate_substabelecimento_pf():
    """
    Gera um substabelecimento para Pessoa Física em formato PDF
    """
    data = request.get_json()
    
    # Dados do OUTORGANTE (PF)
    outorgante_nome = data.get("outorganteNome", "")
    outorgante_nacionalidade = data.get("outorganteNacionalidade", "")
    outorgante_cpf = data.get("outorganteCpf", "")
    outorgante_endereco = remover_cep(data.get("outorganteEndereco", ""))
    
    # Dados do OUTORGADO (PF)
    outorgado_nome = data.get("outorgadoNome", "")
    outorgado_nacionalidade = data.get("outorgadoNacionalidade", "")
    outorgado_cpf = data.get("outorgadoCpf", "")
    outorgado_endereco = remover_cep(data.get("outorgadoEndereco", ""))
    
    # Dados do VEÍCULO
    veiculo_nome = data.get("veiculoNome", "")
    veiculo_placa = data.get("veiculoPlaca", "")
    veiculo_renavam = data.get("veiculoRenavam", "")
    veiculo_chassi = data.get("veiculoChassi", "")
    veiculo_ano_modelo = data.get("veiculoAnoModelo", "")
    veiculo_cor = data.get("veiculoCor", "")
    
    local_emissao = data.get("localEmissao", "")
    data_emissao = data.get("dataEmissao", "")
    
    # Converter data
    if data_emissao:
        try:
            data_obj = datetime.strptime(data_emissao, "%Y-%m-%d")
            data_emissao = data_obj.strftime("%d/%m/%Y")
        except ValueError:
            pass
    
    # Poderes customizáveis
    poderes = data.get("poderes", PODERES_SUBSTABELECIMENTO)
    
    # Criar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    # Título
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "SUBSTABELECIMENTO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGANTE - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGANTE: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{outorgante_nome}, {outorgante_nacionalidade}, maior, inscrito sob o CPF: {outorgante_cpf}, residente e domiciliado em {outorgante_endereco}.")
    pdf.ln(8)

    # NOMEIO E CONSTITUO
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 5, "NOMEIO E CONSTITUO MEU BASTANTE PROCURADOR", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGADOS - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGADOS: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{outorgado_nome}, {outorgado_nacionalidade}, maior, inscrito sob o CPF: {outorgado_cpf}, residente e domiciliado em {outorgado_endereco}.")
    pdf.ln(8)

    # REPRESENTAÇÃO (Substabelecimento) - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "REPRESENTAÇÃO: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{PODERES_SUBSTABELECIMENTO}. Sob o veículo: {veiculo_nome}, Placa: {veiculo_placa}, RENAVAM: {veiculo_renavam}, CHASSI: {veiculo_chassi}, ANO/MODELO {veiculo_ano_modelo}, cor {veiculo_cor}.")
    pdf.ln(8)

    # LOCAL E DATA - JUSTIFICADO
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, f"{local_emissao}, {data_emissao}.", align="J")
    pdf.ln(15)  # Espaço maior para assinatura

    # Assinatura
    pdf.set_line_width(0.5)
    x_start = 60
    x_end = 150
    y_line = pdf.get_y()
    pdf.line(x_start, y_line, x_end, y_line)
    pdf.ln(2)
    pdf.set_font("Times", "", 10)
    pdf.cell(0, 5, "OUTORGANTE", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf_output = pdf.output(dest="S")
    return send_file(
        io.BytesIO(pdf_output),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="substabelecimento_pf.pdf"
    )


# ============================================================================
# SUBSTABELECIMENTO - PJ
# ============================================================================

@extra_bp.route('/generate_substabelecimento_pj', methods=['POST'])
def generate_substabelecimento_pj():
    """
    Gera um substabelecimento para Pessoa Jurídica em formato PDF
    """
    data = request.get_json()
    
    # Dados do OUTORGANTE (PJ)
    outorgante_razao_social = data.get("outorganteRazaoSocial", "")
    outorgante_cnpj = data.get("outorganteCnpj", "")
    outorgante_endereco = remover_cep(data.get("outorganteEndereco", ""))
    
    # Dados do OUTORGADO (PF)
    outorgado_nome = data.get("outorgadoNome", "")
    outorgado_nacionalidade = data.get("outorgadoNacionalidade", "")
    outorgado_cpf = data.get("outorgadoCpf", "")
    outorgado_endereco = remover_cep(data.get("outorgadoEndereco", ""))
    
    # Dados do VEÍCULO
    veiculo_nome = data.get("veiculoNome", "")
    veiculo_placa = data.get("veiculoPlaca", "")
    veiculo_renavam = data.get("veiculoRenavam", "")
    veiculo_chassi = data.get("veiculoChassi", "")
    veiculo_ano_modelo = data.get("veiculoAnoModelo", "")
    veiculo_cor = data.get("veiculoCor", "")
    
    local_emissao = data.get("localEmissao", "")
    data_emissao = data.get("dataEmissao", "")
    
    # Converter data
    if data_emissao:
        try:
            data_obj = datetime.strptime(data_emissao, "%Y-%m-%d")
            data_emissao = data_obj.strftime("%d/%m/%Y")
        except ValueError:
            pass
    
    # Poderes customizáveis
    poderes = data.get("poderes", PODERES_SUBSTABELECIMENTO)
    
    # Criar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    # Título
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, "SUBSTABELECIMENTO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGANTE (PJ) - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGANTE: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{outorgante_razao_social}, inscrito sob o CNPJ: {outorgante_cnpj}, estabelecida em {outorgante_endereco}.")
    pdf.ln(8)

    # NOMEIO E CONSTITUO
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 5, "NOMEIO E CONSTITUO MEU BASTANTE PROCURADOR", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGADOS - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGADOS: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{outorgado_nome}, {outorgado_nacionalidade}, maior, inscrito sob o CPF: {outorgado_cpf}, residente e domiciliado em {outorgado_endereco}.")
    pdf.ln(8)

    # REPRESENTAÇÃO (Substabelecimento) - NEGRITO inline + JUSTIFICADO
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "REPRESENTAÇÃO: ")
    pdf.set_font("Times", "", 12)
    pdf.write(5, f"{PODERES_SUBSTABELECIMENTO}. Sob o veículo: {veiculo_nome}, Placa: {veiculo_placa}, RENAVAM: {veiculo_renavam}, CHASSI: {veiculo_chassi}, ANO/MODELO {veiculo_ano_modelo}, cor {veiculo_cor}.")
    pdf.ln(8)

    # LOCAL E DATA - JUSTIFICADO
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, f"{local_emissao}, {data_emissao}.", align="J")
    pdf.ln(15)  # Espaço maior para assinatura

    # Assinatura
    pdf.set_line_width(0.5)
    x_start = 60
    x_end = 150
    y_line = pdf.get_y()
    pdf.line(x_start, y_line, x_end, y_line)
    pdf.ln(2)
    pdf.set_font("Times", "", 10)
    pdf.cell(0, 5, "OUTORGANTE", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf_output = pdf.output(dest="S")
    return send_file(
        io.BytesIO(pdf_output),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="substabelecimento_pj.pdf"
    )

