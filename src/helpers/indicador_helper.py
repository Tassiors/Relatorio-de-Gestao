# src/helpers/indicador_helper.py
from typing import Dict, Any, List

MESES_POR_BIMESTRE: Dict[int, List[str]] = {
    1: ["Janeiro", "Fevereiro"],
    2: ["Março", "Abril"],
    3: ["Maio", "Junho"],
    4: ["Julho", "Agosto"],
    5: ["Setembro", "Outubro"],
    6: ["Novembro", "Dezembro"],
}

BIMESTRE_LABELS: Dict[int, str] = {
    1: "1º Bimestre (Jan-Fev)",
    2: "2º Bimestre (Mar-Abr)",
    3: "3º Bimestre (Mai-Jun)",
    4: "4º Bimestre (Jul-Ago)",
    5: "5º Bimestre (Set-Out)",
    6: "6º Bimestre (Nov-Dez)",
}

TRIMESTRE_MAP: Dict[int, str] = {
    2: "1º Trimestre (Jan-Mar)",
    3: "2º Trimestre (Abr-Jun)",
    5: "3º Trimestre (Jul-Set)",
    6: "4º Trimestre (Out-Dez)",
}

QUADRIMESTRE_MAP: Dict[int, str] = {
    2: "1º Quadrimestre (Jan-Abr)",
    4: "2º Quadrimestre (Mai-Ago)",
    6: "3º Quadrimestre (Set-Dez)",
}

SEMESTRE_MAP: Dict[int, str] = {
    3: "1º Semestre (Jan-Jun)",
    6: "2º Semestre (Jul-Dez)",
}


def obter_configuracao_periodicidade(periodicidade: str, bimestre_numero: int) -> Dict[str, Any]:
    """
    Mapeia a aplicabilidade, quantidade de campos, competências e orientações contextuais
    de um indicador de acordo com sua periodicidade e o bimestre vigente (1 a 6).
    """
    per = (periodicidade or "BIMESTRAL").upper().strip()
    bim = int(bimestre_numero) if bimestre_numero in range(1, 7) else 1

    if per == "MENSAL":
        meses = MESES_POR_BIMESTRE.get(bim, ["Mês 1", "Mês 2"])
        return {
            "periodicidade": "MENSAL",
            "bimestre_numero": bim,
            "aplicavel": True,
            "quantidade_campos": 2,
            "competencias": meses,
            "orientacao": (
                f"Indicador de periodicidade mensal: informe os 2 resultados apurados "
                f"referentes aos meses de {meses[0]} e {meses[1]}."
            ),
        }

    if per == "TRIMESTRAL":
        if bim in TRIMESTRE_MAP:
            comp = TRIMESTRE_MAP[bim]
            return {
                "periodicidade": "TRIMESTRAL",
                "bimestre_numero": bim,
                "aplicavel": True,
                "quantidade_campos": 1,
                "competencias": [comp],
                "orientacao": f"Indicador trimestral: informe o resultado consolidado referente ao {comp}.",
            }
        prox_bim = 2 if bim == 1 else 5
        prox_trim = TRIMESTRE_MAP[prox_bim]
        return {
            "periodicidade": "TRIMESTRAL",
            "bimestre_numero": bim,
            "aplicavel": False,
            "quantidade_campos": 0,
            "competencias": ["Não aplicável a este bimestre"],
            "orientacao": (
                f"Não aplicável a este bimestre. Indicador trimestral: a medição do {prox_trim} "
                f"será solicitada no {prox_bim}º Bimestre."
            ),
        }

    if per == "QUADRIMESTRAL":
        if bim in QUADRIMESTRE_MAP:
            comp = QUADRIMESTRE_MAP[bim]
            return {
                "periodicidade": "QUADRIMESTRAL",
                "bimestre_numero": bim,
                "aplicavel": True,
                "quantidade_campos": 1,
                "competencias": [comp],
                "orientacao": f"Indicador quadrimestral: informe o resultado consolidado referente ao {comp}.",
            }
        prox_bim = bim + 1
        prox_quad = QUADRIMESTRE_MAP.get(prox_bim, "próximo quadrimestre")
        return {
            "periodicidade": "QUADRIMESTRAL",
            "bimestre_numero": bim,
            "aplicavel": False,
            "quantidade_campos": 0,
            "competencias": ["Não aplicável a este bimestre"],
            "orientacao": (
                f"Não aplicável a este bimestre. Indicador quadrimestral: a medição do {prox_quad} "
                f"será solicitada no {prox_bim}º Bimestre."
            ),
        }

    if per == "SEMESTRAL":
        if bim in SEMESTRE_MAP:
            comp = SEMESTRE_MAP[bim]
            return {
                "periodicidade": "SEMESTRAL",
                "bimestre_numero": bim,
                "aplicavel": True,
                "quantidade_campos": 1,
                "competencias": [comp],
                "orientacao": f"Indicador semestral: informe o resultado consolidado referente ao {comp}.",
            }
        prox_bim = 3 if bim < 3 else 6
        prox_sem = SEMESTRE_MAP[prox_bim]
        return {
            "periodicidade": "SEMESTRAL",
            "bimestre_numero": bim,
            "aplicavel": False,
            "quantidade_campos": 0,
            "competencias": ["Não aplicável a este bimestre"],
            "orientacao": (
                f"Não aplicável a este bimestre. Indicador semestral: a medição do {prox_sem} "
                f"será solicitada no {prox_bim}º Bimestre."
            ),
        }

    # Default: BIMESTRAL
    comp = BIMESTRE_LABELS.get(bim, f"{bim}º Bimestre")
    return {
        "periodicidade": "BIMESTRAL",
        "bimestre_numero": bim,
        "aplicavel": True,
        "quantidade_campos": 1,
        "competencias": [comp],
        "orientacao": f"Indicador bimestral: informe o resultado consolidado apurado no {comp}.",
    }


def validar_itens_indicador_bimestre(
    itens_indicador: List[Dict[str, Any]], bimestre_numero: int
) -> List[str]:
    """
    Valida se os itens de indicador de um relatório bimestral atendem às regras de periodicidade
    e justificativa de indisponibilidade. Retorna lista de pendências.
    """
    pendencias: List[str] = []
    for item in itens_indicador:
        per = item.get("periodicidade", "BIMESTRAL")
        cfg = obter_configuracao_periodicidade(per, bimestre_numero)
        if not cfg["aplicavel"] or item.get("nao_aplicavel"):
            continue

        nome = item.get("nome") or f"Indicador #{item.get('indicador_id')}"
        comp = item.get("competencia") or ""
        label = f"{nome} ({comp})" if comp else nome

        if item.get("resultado_indisponivel"):
            just = (item.get("justificativa_indisponibilidade") or "").strip()
            if len(just) < 5:
                pendencias.append(
                    f"Indicador '{label}': informe uma justificativa para o resultado indisponível (mínimo 5 caracteres)."
                )
        else:
            if item.get("valor_apurado") is None:
                pendencias.append(f"Indicador '{label}': valor apurado não foi informado.")

    return pendencias

