from src.interface import main
from contextlib import suppress
from pathlib import Path
import tempfile



arquivo_lock = Path(tempfile.gettempdir(), 'todo_list.lock')
if arquivo_lock.exists():
    print('o programa já esta rodando. saindo.')
    exit()
else:
    with arquivo_lock.open('w') as arquivo:
        arquivo.write('lock')
with suppress(KeyboardInterrupt, EOFError):
    main()
print('\nprograma finalizado')
arquivo_lock.unlink()