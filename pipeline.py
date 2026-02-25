"""Entrypoint leve que delega para o módulo `pipeline_main`.

Este arquivo mantém compatibilidade com execuções diretas de
`python pipeline.py` ao montar logging básico e chamar `Pipeline.run()`.
"""

import logging

from core.pipeline_main import Pipeline


# Configuração básica de logging do módulo (pode ser sobrescrita pela aplicação)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    Pipeline().run()


if __name__ == "__main__":
    main()
