# Programa Eleições Senado

Este programa serve para simular o processo de Eleições do Senado.

O programa pode ser corrido desde a linha de comandos das seguintes formas:

    python elections.py [-h]                               Mostrar uma mensagem de uso e sair
    python elections.py [-icsv fname]                      Importar um documento csv
    python elections.py [-ocsv fname]                      Exportar um documento csv
    python elections.py [-log fname]                       Guardar o log num ficheiro

O ficheiro de importação do csv e os logs também podem ser dados de forma interativa na interface de linha de comandos.

## Dependências:

    argparse
    pandas