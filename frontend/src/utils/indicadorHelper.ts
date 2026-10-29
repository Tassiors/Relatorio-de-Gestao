// frontend/src/utils/indicadorHelper.ts
import type { IndicadorItem } from '../services/gestaoApi';

export interface ConfiguracaoPeriodicidade {
  periodicidade: string;
  bimestreNumero: number;
  aplicavel: boolean;
  quantidadeCampos: number;
  competencias: string[];
  orientacao: string;
}

const MESES_POR_BIMESTRE: Record<number, [string, string]> = {
  1: ['Janeiro', 'Fevereiro'],
  2: ['Março', 'Abril'],
  3: ['Maio', 'Junho'],
  4: ['Julho', 'Agosto'],
  5: ['Setembro', 'Outubro'],
  6: ['Novembro', 'Dezembro']
};

const BIMESTRE_LABELS: Record<number, string> = {
  1: '1º Bimestre (Jan-Fev)',
  2: '2º Bimestre (Mar-Abr)',
  3: '3º Bimestre (Mai-Jun)',
  4: '4º Bimestre (Jul-Ago)',
  5: '5º Bimestre (Set-Out)',
  6: '6º Bimestre (Nov-Dez)'
};

const TRIMESTRE_MAP: Record<number, string> = {
  2: '1º Trimestre (Jan-Mar)',
  3: '2º Trimestre (Abr-Jun)',
  5: '3º Trimestre (Jul-Set)',
  6: '4º Trimestre (Out-Dez)'
};

const QUADRIMESTRE_MAP: Record<number, string> = {
  2: '1º Quadrimestre (Jan-Abr)',
  4: '2º Quadrimestre (Mai-Ago)',
  6: '3º Quadrimestre (Set-Dez)'
};

const SEMESTRE_MAP: Record<number, string> = {
  3: '1º Semestre (Jan-Jun)',
  6: '2º Semestre (Jul-Dez)'
};

export function obterConfiguracaoPeriodicidade(
  periodicidade: string,
  bimestreNumero: number
): ConfiguracaoPeriodicidade {
  const per = (periodicidade || 'BIMESTRAL').toUpperCase().trim();
  const bim = bimestreNumero >= 1 && bimestreNumero <= 6 ? bimestreNumero : 1;

  if (per === 'MENSAL') {
    const meses = MESES_POR_BIMESTRE[bim] || ['Mês 1', 'Mês 2'];
    return {
      periodicidade: 'MENSAL',
      bimestreNumero: bim,
      aplicavel: true,
      quantidadeCampos: 2,
      competencias: [...meses],
      orientacao: `Indicador de periodicidade mensal: informe os 2 resultados apurados referentes aos meses de ${meses[0]} e ${meses[1]}.`
    };
  }

  if (per === 'TRIMESTRAL') {
    if (TRIMESTRE_MAP[bim]) {
      const comp = TRIMESTRE_MAP[bim];
      return {
        periodicidade: 'TRIMESTRAL',
        bimestreNumero: bim,
        aplicavel: true,
        quantidadeCampos: 1,
        competencias: [comp],
        orientacao: `Indicador trimestral: informe o resultado consolidado referente ao ${comp}.`
      };
    }
    const proxBim = bim === 1 ? 2 : 5;
    const proxTrim = TRIMESTRE_MAP[proxBim];
    return {
      periodicidade: 'TRIMESTRAL',
      bimestreNumero: bim,
      aplicavel: false,
      quantidadeCampos: 0,
      competencias: ['Não aplicável a este bimestre'],
      orientacao: `Não aplicável a este bimestre. Indicador trimestral: a medição do ${proxTrim} será solicitada no ${proxBim}º Bimestre.`
    };
  }

  if (per === 'QUADRIMESTRAL') {
    if (QUADRIMESTRE_MAP[bim]) {
      const comp = QUADRIMESTRE_MAP[bim];
      return {
        periodicidade: 'QUADRIMESTRAL',
        bimestreNumero: bim,
        aplicavel: true,
        quantidadeCampos: 1,
        competencias: [comp],
        orientacao: `Indicador quadrimestral: informe o resultado consolidado referente ao ${comp}.`
      };
    }
    const proxBim = bim + 1;
    const proxQuad = QUADRIMESTRE_MAP[proxBim] || 'próximo quadrimestre';
    return {
      periodicidade: 'QUADRIMESTRAL',
      bimestreNumero: bim,
      aplicavel: false,
      quantidadeCampos: 0,
      competencias: ['Não aplicável a este bimestre'],
      orientacao: `Não aplicável a este bimestre. Indicador quadrimestral: a medição do ${proxQuad} será solicitada no ${proxBim}º Bimestre.`
    };
  }

  if (per === 'SEMESTRAL') {
    if (SEMESTRE_MAP[bim]) {
      const comp = SEMESTRE_MAP[bim];
      return {
        periodicidade: 'SEMESTRAL',
        bimestreNumero: bim,
        aplicavel: true,
        quantidadeCampos: 1,
        competencias: [comp],
        orientacao: `Indicador semestral: informe o resultado consolidado referente ao ${comp}.`
      };
    }
    const proxBim = bim < 3 ? 3 : 6;
    const proxSem = SEMESTRE_MAP[proxBim];
    return {
      periodicidade: 'SEMESTRAL',
      bimestreNumero: bim,
      aplicavel: false,
      quantidadeCampos: 0,
      competencias: ['Não aplicável a este bimestre'],
      orientacao: `Não aplicável a este bimestre. Indicador semestral: a medição do ${proxSem} será solicitada no ${proxBim}º Bimestre.`
    };
  }

  const comp = BIMESTRE_LABELS[bim] || `${bim}º Bimestre`;
  return {
    periodicidade: 'BIMESTRAL',
    bimestreNumero: bim,
    aplicavel: true,
    quantidadeCampos: 1,
    competencias: [comp],
    orientacao: `Indicador bimestral: informe o resultado consolidado apurado no ${comp}.`
  };
}

export function normalizarItensIndicadorParaBimestre(
  itens: IndicadorItem[],
  bimestreNumero: number
): IndicadorItem[] {
  const porIndicador = new Map<number, IndicadorItem[]>();
  for (const item of itens || []) {
    const lista = porIndicador.get(item.indicador_id) || [];
    lista.push(item);
    porIndicador.set(item.indicador_id, lista);
  }

  const resultado: IndicadorItem[] = [];
  for (const [, grupo] of porIndicador.entries()) {
    const base = grupo[0];
    const cfg = obterConfiguracaoPeriodicidade(base.periodicidade, bimestreNumero);

    if (cfg.periodicidade === 'MENSAL') {
      cfg.competencias.forEach((mesNome, idx) => {
        const existente =
          grupo.find((g) => g.competencia === mesNome) ||
          (grupo.length === 1 && idx === 0 ? grupo[0] : undefined);
        resultado.push({
          ...base,
          ...(existente || {}),
          id: existente?.id ?? null,
          competencia: mesNome,
          valor_apurado: existente ? existente.valor_apurado : null,
          meta_atingida: existente ? existente.meta_atingida : null,
          resultado_indisponivel: existente ? Boolean(existente.resultado_indisponivel) : false,
          justificativa_indisponibilidade: existente?.justificativa_indisponibilidade || '',
          nao_aplicavel: false,
          orientacao_periodicidade: cfg.orientacao
        });
      });
    } else {
      const compEsperada = cfg.competencias[0];
      resultado.push({
        ...base,
        competencia: compEsperada,
        nao_aplicavel: !cfg.aplicavel,
        orientacao_periodicidade: cfg.orientacao
      });
    }
  }

  return resultado;
}

