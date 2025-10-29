import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)


class FileUtils:
    """Utilitários de I/O: leitura segura e escrita de arquivos."""

    @staticmethod
    def safe_read_text(path: str, encodings: Optional[List[str]] = None) -> str:
        if encodings is None:
            encodings = [
                "utf-8",
                "utf-8-sig",
                "utf-16",
                "utf-16-le",
                "utf-16-be",
                "cp1252",
                "latin-1",
            ]
        with open(path, "rb") as fh:
            raw = fh.read()

        text = None
        for enc in encodings:
            try:
                text = raw.decode(enc)
                break
            except Exception:
                continue

        if text is None:
            text = raw.decode("utf-8", errors="replace")

        if "\x00" in text:
            text = text.replace("\x00", "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [ln.rstrip() for ln in text.split("\n")]
        text = "\n".join(lines)
        text = text.strip("\n") + ("\n" if text.endswith("\n") else "")
        MAX_CHARS = 500_000
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS]
        return text

    @staticmethod
    def load_markdown_file(path: str) -> str:
        logger.info("Iniciando: load_markdown_file -> %s", path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.info("Finalizado: load_markdown_file -> %s", path)
                return content
        except FileNotFoundError:
            logger.warning("Arquivo não encontrado: %s", path)
            logger.info("Finalizado (com erro): load_markdown_file -> %s", path)
            return ""
        except Exception as e:
            logger.exception("Erro ao ler arquivo %s: %s", path, e)
            logger.info("Finalizado (com erro): load_markdown_file -> %s", path)
            return ""

    @staticmethod
    def write_text_file(path: str, text: str) -> None:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            logger.exception("Erro ao salvar arquivo %s: %s", path, e)
