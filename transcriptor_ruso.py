import re
import sys
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Intentamos importar el motor de acentuación mediante PLN
try:
    from ruaccent import RUAccent
    HAS_NLP = True
except ImportError:
    HAS_NLP = False


# ============================================================================
# CONFIGURACIÓN FILOLÓGICA SRH
# ============================================================================
@dataclass
class OpcionesSRH:
    """Configuración de las variables mutables de la Norma SRH."""
    colapsar_dobles_consonantes: bool = True


# ============================================================================
# TILDADOR RAE (NÚCLEO ORTOGRÁFICO)
# ============================================================================
VocalIndexada = Tuple[int, str]
NucleoSilabico = List[VocalIndexada]

class TildadorRAE:
    """Motor de acentuación ortográfica estricto de la Real Academia Española."""
    
    VOCALES_FONETICAS = frozenset("aeiouyáéíóúü")
    ABIERTAS          = frozenset("aeoáéó")
    CERRADAS          = frozenset("iuíúüy")

    TILDE = {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú', 'y': 'ý', 'ü': 'ú'}

    def __init__(self, y_extranjera: bool = False, h_aspirada: bool = False) -> None:
        self.y_extranjera = y_extranjera
        self.h_aspirada   = h_aspirada

    def _es_vocal_fonetica(self, char: str, pos: int, word: str) -> bool:
        c = char.lower()
        w_len = len(word)
        if c not in self.VOCALES_FONETICAS: return False
        if c == 'y' and pos + 1 < w_len and word[pos + 1].lower() in self.VOCALES_FONETICAS: return False
        if c == 'u' and char != 'ü' and pos > 0 and word[pos - 1].lower() in "qg":
            if pos + 1 < w_len and word[pos + 1].lower() in "eiéí": return False
        return True

    def _son_adyacentes(self, idx1: int, idx2: int, word: str) -> bool:
        if idx2 - idx1 == 1: return True
        intermedio = word[idx1 + 1 : idx2].lower()
        if self.h_aspirada: return False
        return intermedio == 'h' * len(intermedio)

    def _clase_vocal(self, char: str, es_tonica: bool) -> str:
        c = char.lower()
        if c in self.ABIERTAS: return 'A'
        if c in "íúý":         return 'Ct'
        if c in "iuüy":        return 'Ct' if es_tonica else 'Ca'
        return ''

    def _extraer_vocales(self, word: str) -> List[VocalIndexada]:
        vocales: List[VocalIndexada] = []
        stress_found = False

        for i, char in enumerate(word):
            if not self._es_vocal_fonetica(char, i, word): continue
            if char.isupper() and not stress_found:
                vocales.append((i, char))
                stress_found = True
            else:
                vocales.append((i, char.lower()))

        procesadas: List[VocalIndexada] = []
        k = 0
        while k < len(vocales):
            idx, char = vocales[k]
            if char.isupper() and char.lower() in "iuü" and k + 1 < len(vocales):
                idx_next, char_next = vocales[k + 1]
                c1 = char.lower().replace('ü', 'u').replace('y', 'i')
                c2 = char_next.lower().replace('ü', 'u').replace('y', 'i')
                if c2 in "iu" and c1 != c2 and self._son_adyacentes(idx, idx_next, word):
                    procesadas.extend([(idx, char.lower()), (idx_next, char_next.upper())])
                    k += 2
                    continue
            procesadas.append((idx, char))
            k += 1
        return procesadas

    def _debe_separarse(self, nucleo_actual: NucleoSilabico, vocales: List[VocalIndexada], k: int, word: str) -> bool:
        v_prev, v_curr = nucleo_actual[-1], vocales[k]
        t_prev = self._clase_vocal(v_prev[1], v_prev[1].isupper())
        t_curr = self._clase_vocal(v_curr[1], v_curr[1].isupper())

        if t_prev == 'A' and t_curr in ('A', 'Ct'): return True
        if t_prev == 'Ct' and t_curr == 'A': return True
        if v_prev[1].lower() == v_curr[1].lower(): return True

        t_next = None
        if k + 1 < len(vocales) and self._son_adyacentes(v_curr[0], vocales[k + 1][0], word):
            t_next = self._clase_vocal(vocales[k + 1][1], vocales[k + 1][1].isupper())

        if t_prev == 'A' and t_curr in ('Ca', 'Ct') and t_next in ('Ca', 'Ct'): return True
        if len(nucleo_actual) >= 2:
            t_prev2 = self._clase_vocal(nucleo_actual[-2][1], nucleo_actual[-2][1].isupper())
            if t_prev2 in ('Ca', 'Ct') and t_prev in ('Ca', 'Ct') and t_curr == 'A': return True
            if t_prev2 == 'A' and t_prev in ('Ca', 'Ct') and t_curr == 'A': return True
            if t_prev2 in ('Ca', 'Ct') and t_prev in ('Ca', 'Ct') and t_curr in ('Ca', 'Ct'): return True
        return False

    def _silabear(self, vocales: List[VocalIndexada], word: str) -> List[NucleoSilabico]:
        if not vocales: return []
        nucleos: List[NucleoSilabico] = []
        nucleo_actual: NucleoSilabico = [vocales[0]]

        for k in range(1, len(vocales)):
            v_prev, v_curr = nucleo_actual[-1], vocales[k]
            if not self._son_adyacentes(v_prev[0], v_curr[0], word):
                nucleos.append(nucleo_actual)
                nucleo_actual = [v_curr]
                continue
            if self._debe_separarse(nucleo_actual, vocales, k, word):
                nucleos.append(nucleo_actual)
                nucleo_actual = [v_curr]
            else:
                nucleo_actual.append(v_curr)
        nucleos.append(nucleo_actual)
        return nucleos

    def _detectar_hiato_acentual(self, vocales: List[VocalIndexada], stress_char_idx: int, word: str) -> bool:
        idx_tonica = next(i for i, v in enumerate(vocales) if v[0] == stress_char_idx)
        v_tonica = vocales[idx_tonica][1].lower()
        if v_tonica not in "iuyü": return False
        if idx_tonica > 0:
            v_ant = vocales[idx_tonica - 1]
            if self._son_adyacentes(v_ant[0], stress_char_idx, word) and v_ant[1].lower() in self.ABIERTAS: return True
        if idx_tonica < len(vocales) - 1:
            v_sig = vocales[idx_tonica + 1]
            if self._son_adyacentes(stress_char_idx, v_sig[0], word) and v_sig[1].lower() in self.ABIERTAS: return True
        return False

    def _necesita_tilde(self, nucleos: List[NucleoSilabico], stress_nuc_idx: int, word: str, is_hiato: bool) -> bool:
        if is_hiato: return True
        if len(nucleos) == 1: return False

        clean_word = "".join(filter(str.isalpha, word)).lower()
        if not clean_word: return False

        last_char = clean_word[-1]
        es_y_ext = self.y_extranjera and last_char == 'y' and len(clean_word) >= 2 and clean_word[-2] not in self.VOCALES_FONETICAS
        ends_in_vowel = last_char in "aeiou" or es_y_ext
        ends_in_cluster = len(clean_word) >= 2 and not ends_in_vowel and clean_word[-2] not in "aeiou"

        pos_from_end = len(nucleos) - 1 - stress_nuc_idx
        if pos_from_end == 0: return not ends_in_cluster and (ends_in_vowel or last_char in 'ns')
        if pos_from_end == 1: return ends_in_cluster or (not ends_in_vowel and last_char not in 'ns')
        return True

    def _resolver_diana(self, nucleos: List[NucleoSilabico], stress_nuc_idx: int, stress_char_idx: int, needs_tilde: bool, is_hiato: bool) -> int:
        if not needs_tilde: return stress_char_idx
        nuc_vocales = nucleos[stress_nuc_idx]
        nuc_str = "".join(v[1].lower() for v in nuc_vocales)
        if nuc_str in ("ui", "iu"): return nuc_vocales[1][0]
        if len(nuc_vocales) > 1 and not is_hiato:
            return next((v_idx for v_idx, char in nuc_vocales if char.lower() in self.ABIERTAS), stress_char_idx)
        return stress_char_idx

    def _renderizar(self, word: str, diana_idx: int, needs_tilde: bool) -> str:
        return "".join(
            self.TILDE.get(char.lower(), char.lower()) if idx == diana_idx and needs_tilde else char.lower()
            for idx, char in enumerate(word)
        )

    def aplicar(self, word: str) -> str:
        if not word: return ""
        vocales = self._extraer_vocales(word)
        if not any(v[1].isupper() for v in vocales): return word.lower()

        stress_char_idx = next(v[0] for v in vocales if v[1].isupper())
        nucleos = self._silabear(vocales, word)
        stress_nuc_idx = next(j for j, nuc in enumerate(nucleos) if any(idx == stress_char_idx for idx, _ in nuc))
        is_hiato = self._detectar_hiato_acentual(vocales, stress_char_idx, word)
        needs_tilde = self._necesita_tilde(nucleos, stress_nuc_idx, word, is_hiato)
        diana_idx = self._resolver_diana(nucleos, stress_nuc_idx, stress_char_idx, needs_tilde, is_hiato)

        return self._renderizar(word, diana_idx, needs_tilde)


# ============================================================================
# TRANSCRIPTOR RUSO-ESPAÑOL (NORMA SRH)
# ============================================================================
class TranscriptorSRH:
    """
    Transcriptor automático ruso → español. Norma SRH (Versión Definitiva).
    Filológicamente estricto. Implementa la asimilación velar, el colapso de
    falsos hiatos y el arbitraje ortográfico de la RAE de forma incondicional.
    """

    VOCALES_RUSAS = frozenset("аеёиоуыэюя")
    SIBILANTES    = frozenset("жшчщц")
    SIGNOS        = frozenset("ъь")
    BILABIALES    = frozenset("бп") # Evita falsos positivos con cadenas vacías

    def __init__(self, use_nlp: bool = True, opciones: Optional[OpcionesSRH] = None):
        self.use_nlp: bool = use_nlp and HAS_NLP
        self.opciones: OpcionesSRH = opciones or OpcionesSRH()
        self.motor_pln: Optional["RUAccent"] = None
        self.tildador = TildadorRAE()

        if self.use_nlp:
            self.motor_pln = self._inicializar_motor_pln()

    def _inicializar_motor_pln(self) -> Optional["RUAccent"]:
        print("\n[Sistema] Despertando el motor neuronal (ruaccent)...")
        motor = RUAccent()
        motor.load(omograph_model_size='big_poetry', use_dictionary=True)
        logging.info("[Ok] Red neuronal activada.")
        return motor

    def _normalizar_acento_nlp(self, texto: str, motor_pln: "RUAccent") -> str:
        try:
            texto_acentuado = motor_pln.process_all(texto)
            res, i = "", 0
            while i < len(texto_acentuado):
                if texto_acentuado[i] == '+':
                    if i + 1 < len(texto_acentuado):
                        res += texto_acentuado[i + 1] + '\u0301'
                        i += 2
                    else:
                        i += 1
                else:
                    res += texto_acentuado[i]
                    i += 1
            return res
        except Exception:
            logging.warning("[Aviso PLN] Interrupción Neuronal: error al procesar la prosodia.")
            return texto

    def _transcribir_palabra(self, palabra: str, uso_pln: bool = False) -> str:
        if not palabra: return ""

        chars = list(palabra)
        normalized, stress_idx = [], -1
        
        # 1. Extracción de acento prosódico
        for char in chars:
            if char == '\u0301':
                if normalized: stress_idx = len(normalized) - 1
            else:
                normalized.append(char)

        # 1.1 Diagnóstico Tónico Elegante
        origen_acento = "Por defecto (No detectado)"
        if stress_idx != -1:
            origen_acento = "Red Neuronal (PLN)" if uso_pln else "Explícito (Usuario)"
        else:
            for i, char in enumerate(normalized):
                if char.lower() == 'ё':
                    stress_idx = i
                    origen_acento = "Nativo (Letra Ё)"
                    break
        
        # Reconstrucción visual prístina de la palabra tildad
        palabra_visual = "".join(normalized)
        if stress_idx != -1 and normalized[stress_idx].lower() != 'ё':
            palabra_visual = palabra_visual[:stress_idx + 1] + '\u0301' + palabra_visual[stress_idx + 1:]

        if any(c.isalpha() for c in palabra_visual):
            logging.info(f" └─ Acento tónico en '{palabra_visual}': {origen_acento}")

        n = len(normalized)
        res_intermediate = ""
        casing_mask = []

        def would_generate_i(sign_c: str, pos: int) -> bool:
            if pos + 1 >= n: return False
            nxt_v = normalized[pos + 1].lower()
            if sign_c == 'ь' and nxt_v in self.VOCALES_RUSAS and nxt_v != 'и': return True
            if sign_c == 'ъ' and nxt_v in 'еёюя': return True
            return False

        # 2. Transcripción morfológica central
        i = 0
        while i < n:
            c_orig = normalized[i]
            c = c_orig.lower()
            is_upper = c_orig.isupper()
            is_stressed = (i == stress_idx)
            prev = normalized[i - 1].lower() if i > 0 else ''

            # Regla 2.3: Colapso de consonantes dobles (Mutable)
            if self.opciones.colapsar_dobles_consonantes:
                if i > 0 and c == prev and c not in self.VOCALES_RUSAS and c not in 'ъьй':
                    if c != 'р':
                        i += 1
                        continue

            # Regla 2.1.2: Signos Ortográficos
            if c in self.SIGNOS:
                if would_generate_i(c, i):
                    out = 'i' 
                else:
                    i += 1
                    continue
            
            # Regla 2.4: Colapso ИЙ / ЫЙ (Falsos Hiatos) - [Incondicional]
            elif c in 'иы' and i + 1 < n and normalized[i + 1].lower() == 'й':
                nxt_after = normalized[i + 2].lower() if i + 2 < n else ''
                if not (nxt_after in self.VOCALES_RUSAS):
                    is_stressed_group = (i == stress_idx or i + 1 == stress_idx)
                    out = 'I' if is_stressed_group else 'i'
                    
                    is_upper_group = normalized[i].isupper() or normalized[i+1].isupper()
                    casing_mask.append(is_upper_group)
                    res_intermediate += out
                    i += 2
                    continue
                else:
                    out = 'I' if is_stressed else 'i'

            # El Eje Vocálico y Consonántico
            else:
                out = ""
                
                # --- Vocales Puras ---
                if c == 'а': out = 'A' if is_stressed else 'a'
                elif c == 'о': out = 'O' if is_stressed else 'o'
                elif c == 'э': out = 'E' if is_stressed else 'e'
                elif c in 'иы': out = 'I' if is_stressed else 'i'
                
                # --- Diéresis de la У ---
                elif c == 'у':
                    nuc_norm = 'U' if is_stressed else 'u'
                    nuc_dier = 'Ü' if is_stressed else 'ü'
                    if prev == 'г' and i + 1 < n:
                        nxt_c = normalized[i + 1].lower()
                        do_dieresis = nxt_c in 'эеий'
                        if not do_dieresis and nxt_c in self.SIGNOS:
                            do_dieresis = would_generate_i(nxt_c, i + 1)
                        out = nuc_dier if do_dieresis else nuc_norm
                    else:
                        out = nuc_norm

                # --- La semivocal Й ---
                elif c == 'й':
                    is_ante_vocal = i + 1 < n and (normalized[i + 1].lower() in self.VOCALES_RUSAS)
                    out = ('Y' if is_stressed else 'y') if is_ante_vocal else ('I' if is_stressed else 'i')

                # --- Vocales Iotadas (Е, Ё, Ю, Я) ---
                elif c == 'е':
                    nuc = 'E' if is_stressed else 'e'
                    if not prev or (prev in self.VOCALES_RUSAS and prev not in 'иый'): out = 'y' + nuc
                    else: out = nuc
                        
                elif c in 'ёюя':
                    nuc_val = {'ё': 'o', 'ю': 'u', 'я': 'a'}[c]
                    nuc = nuc_val.upper() if is_stressed else nuc_val
                    if not prev or (prev in self.VOCALES_RUSAS and prev not in 'иый'): out = 'y' + nuc
                    elif prev in 'йъь' or prev in self.SIBILANTES or prev in 'иы': out = nuc
                    else: out = 'i' + nuc

                # --- Consonantes ---
                elif c == 'б': out = 'b'
                elif c == 'в': out = 'v'
                elif c == 'д': out = 'd'
                elif c == 'ж': out = 'zh'
                elif c == 'з': out = 'z'
                elif c == 'к': out = 'k'
                elif c == 'л': out = 'l'
                elif c == 'м': out = 'm'
                elif c == 'п': out = 'p'
                elif c == 'р': out = 'r'
                elif c == 'с': out = 's'
                elif c == 'т': out = 't'
                elif c == 'ф': out = 'f'
                elif c == 'х': out = 'j'
                elif c == 'ц': out = 'ts'
                elif c == 'ч': out = 'ch'
                elif c == 'ш': out = 'sh'
                elif c == 'щ': out = 'shch'
                
                # --- Asimilación Nasal (Н) ---
                elif c == 'н':
                    nxt_c = normalized[i + 1].lower() if i + 1 < n else ''
                    out = 'm' if nxt_c in self.BILABIALES else 'n'

                # --- Protección Velar (Г) ---
                elif c == 'г':
                    do_gu = False
                    if i + 1 < n:
                        nxt_c = normalized[i + 1].lower()
                        if nxt_c in 'еёиэюяый': do_gu = True
                        elif nxt_c in self.SIGNOS:
                            if would_generate_i(nxt_c, i + 1): do_gu = True
                            elif i + 2 < n and normalized[i + 2].lower() in 'еёиэюяый': do_gu = True
                    out = 'gu' if do_gu else 'g'
                else:
                    out = c

            # 3. Aplicación y registro de la máscara de mayúsculas (Casing Mask)
            out_len = len(out)
            if out_len > 0:
                if is_upper:
                    prev_upper = (i > 0 and normalized[i - 1].isupper())
                    next_upper = (i < n - 1 and normalized[i + 1].isupper())
                    if next_upper or (prev_upper and i == n - 1):
                        casing_mask.extend([True] * out_len)
                    else:
                        casing_mask.extend([True] + [False] * (out_len - 1))
                else:
                    casing_mask.extend([False] * out_len)
            
            res_intermediate += out
            i += 1

        # 4. El Tribunal (Aplicación del Tildador RAE)
        final_word_base = self.tildador.aplicar(res_intermediate)

        # 5. Renderizado Estético Final
        final_word = ""
        for char, mask_upper in zip(final_word_base, casing_mask):
            final_word += char.upper() if mask_upper else char

        return final_word

    def transcribir(self, texto_ruso: str) -> str:
        if not texto_ruso: return ""

        texto_procesado = texto_ruso
        uso_pln = False
        contiene_cirilico = any('\u0400' <= c <= '\u04FF' for c in texto_ruso)

        # El motor PLN solo despierta si hay texto cirílico y no hay acentos explícitos
        if self.motor_pln and contiene_cirilico and '\u0301' not in texto_ruso and 'ё' not in texto_ruso.lower():
            texto_procesado = self._normalizar_acento_nlp(texto_ruso, self.motor_pln)
            uso_pln = True

        parts = re.split(r'([^\w\u0301]+)', texto_procesado)
        result_parts = []
        for part in parts:
            if any('\u0400' <= c <= '\u04FF' or c in 'ёЁ\u0301' for c in part):
                result_parts.append(self._transcribir_palabra(part, uso_pln))
            else:
                result_parts.append(part)
        return ''.join(result_parts)


# ============================================================================
# CONSOLA INTERACTIVA (CLI)
# ============================================================================
if __name__ == "__main__":
    # Configuración de logging limpia y elegante para la consola
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("=" * 75)
    print(" TRANSCRIPTOR AUTOMÁTICO RUSO-ESPAÑOL (NORMA SRH - VERSIÓN DEFINITIVA)")
    print("=" * 75)

    config = OpcionesSRH(colapsar_dobles_consonantes=True)
    transcriptor = TranscriptorSRH(use_nlp=True, opciones=config)

    print(f"Simplificación de consonantes: {'ACTIVA' if config.colapsar_dobles_consonantes else 'INACTIVA'}")
    print("-" * 75)
    print("Escribe en ruso y presiona Enter. ('salir' para finalizar)")
    print("-" * 75)

    while True:
        try:
            entrada = input("\n[Ruso] >>> ").strip()
            if entrada.lower() == 'salir': break
            if not entrada: continue
            
            resultado = transcriptor.transcribir(entrada)
            print(f"[Español SRH] ======>> {resultado}")
        except (KeyboardInterrupt, EOFError): break
        except Exception as e:
            logging.error(f"Error: {e}")