from flask import Blueprint, request, send_file
from fpdf import FPDF
import io
from datetime import datetime
import re

# Constantes de poderes
PODERES_PROCURACAO = """Podendo, para tanto, o dito procurador representar o outorgante perante o CRVA/DETRAN, para fins de transferência de propriedade podendo vender para si e/ou para terceiros, fazer comunicação de venda, conferindo-lhe poderes específicos para, em seu nome, receber o valor decorrente da venda, assinar o campo de acordo no CRV, solicitar a ativação ou baixa do veículo, assinar requerimentos de alteração de características e informações do veículo, inclusive troca de motor ou restrições fiduciárias, reclassificar o veículo para média monta, recuperar de sinistro, requerer processo de desbloqueio de veículo acidentado, realizar troca de município, incluir alienação em favor do outorgante, endossar documentação, alienar fiduciariamente ou firmar contrato de reserva de domínio, seja para si ou para terceiros, emitir ou cancelar ATPV-e, assinar tanto no campo de comprador quanto no de vendedor da ATPV-e, inclusive solicitar segunda via da ATPV-e, bem como emitir o CRLV-e, alterar endereço de postagem, assinar declaração de endereço, solicitar liberação para laudo no INMETRO (CSV), usar o veículo em qualquer parte do território nacional ou estrangeiro, remover o veículo de depósito (CRD), solicitar e retirar D.C.P.P.O., solicitar placas e vistorias, retirar documentos nos Correios, praticar todos os atos necessários para uso e gozo do veículo como coisa própria, sem interferência de terceiros, requerendo, promovendo e assinando o que se fizer necessário, inclusive assinando declarações de responsabilidade pela procedência de motor, carroceria e chassi, declarações de difícil acesso à coleta do número do motor e declarações de perda de plaquetas."""

def remover_cep(endereco):
    """Remove CEP do endereço"""
    if not endereco:
        return endereco
    return re.sub(r',?\s*CEP:?\s*\d{5}-?\d{3}', '', endereco, flags=re.IGNORECASE)

test_bp = Blueprint('test', __name__)

@test_bp.route('/test_multiplos', methods=['POST'])
def test_procuracao_pf_multiplos():
    """
    Teste de procuração PF múltiplos com espaçamento correto
    """
    data = request.get_json()
    
    outorgante_nome = data.get("outorganteNome", "")
    outorgante_nacionalidade = data.get("outorganteNacionalidade", "")
    outorgante_cpf = data.get("outorganteCpf", "")
    outorgante_endereco = remover_cep(data.get("outorganteEndereco", ""))
    
    outorgados = data.get("outorgados", [])
    
    veiculo_nome = data.get("veiculoNome", "")
    veiculo_placa = data.get("veiculoPlaca", "")
    veiculo_renavam = data.get("veiculoRenavam", "")
    veiculo_chassi = data.get("veiculoChassi", "")
    veiculo_ano_modelo = data.get("veiculoAnoModelo", "")
    veiculo_cor = data.get("veiculoCor", "")
    
    local_emissao = data.get("localEmissao", "")
    data_emissao = data.get("dataEmissao", "")
    
    if data_emissao:
        try:
            data_obj = datetime.strptime(data_emissao, "%Y-%m-%d")
            data_emissao = data_obj.strftime("%d/%m/%Y")
        except ValueError:
            pass
    
    poderes = data.get("poderes", PODERES_PROCURACAO)

    # Criar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    # Título
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 8, "PROCURAÇÃO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # OUTORGANTE - Usar multi_cell com markdown inline
    pdf.set_font("Times", "", 12)
    outorgante_texto = f"OUTORGANTE: {outorgante_nome}, {outorgante_nacionalidade}, maior, inscrito sob o CPF: {outorgante_cpf}, residente e domiciliado em {outorgante_endereco}."
    
    # Renderizar com negrito inline
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGANTE: ")
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, f"{outorgante_nome}, {outorgante_nacionalidade}, maior, inscrito sob o CPF: {outorgante_cpf}, residente e domiciliado em {outorgante_endereco}.", align="J")
    pdf.ln(5)

    # NOMEIO E CONSTITUO
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 5, "NOMEIO E CONSTITUO MEU BASTANTE PROCURADOR", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # OUTORGADOS
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
    
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "OUTORGADOS: ")
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, outorgados_texto, align="J")
    pdf.ln(5)

    # REPRESENTAÇÃO
    representacao_texto = f"para fim especial, podendo vender para si e/ou para terceiros um {veiculo_nome}, Placa: {veiculo_placa}, RENAVAM: {veiculo_renavam}, CHASSI: {veiculo_chassi}, ANO/MODELO {veiculo_ano_modelo}, cor {veiculo_cor}."
    
    pdf.set_font("Times", "B", 12)
    pdf.write(5, "REPRESENTAÇÃO: ")
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, representacao_texto, align="J")
    pdf.ln(5)

    # PODERES
    pdf.set_font("Times", "", 12)
    pdf.multi_cell(0, 5, poderes, align="J")
    pdf.ln(5)

    # LOCAL E DATA
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
    pdf.cell(0, 5, "Assinatura do Outorgante", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf_output = pdf.output(dest="S")
    return send_file(
        io.BytesIO(pdf_output),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="teste_multiplos.pdf"
    )

