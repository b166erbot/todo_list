import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk, AyatanaAppIndicator3 as appindicator
import shelve
from contextlib import suppress
from functools import partial


class TodoList(Gtk.Window):
    def __init__(self):
        super().__init__(title = 'Todo List')
        
        box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 2)
        self.add(box)

        scrolled_window = Gtk.ScrolledWindow()
        box.add(scrolled_window)
        scrolled_window.set_min_content_width(400)
        scrolled_window.set_min_content_height(250)

        tree_view = Gtk.TreeView()
        self._liststore = Gtk.ListStore(bool, str)
        tree_view.set_model(self._liststore)
        render_cell_toggle = Gtk.CellRendererToggle()
        coluna0 = Gtk.TreeViewColumn(
            title = 'tarefa realizada',
            cell_renderer = render_cell_toggle,
            active = 0
        )
        coluna1 = Gtk.TreeViewColumn(
            title = 'texto',
            cell_renderer = Gtk.CellRendererText(),
            text = 1
        )
        tree_view.append_column(coluna0)
        tree_view.append_column(coluna1)
        scrolled_window.add_with_viewport(tree_view)

        self._selecao = tree_view.get_selection()

        banco = shelve.open('save.pkl')
        for item in banco.get('tarefas', []):
            self._liststore.append(item)
        
        self.botao_adicionar = Gtk.Button(label = 'adicionar')
        self.botao_remover = Gtk.Button(label = 'remover')
        self.entry = Gtk.Entry()
        
        box_entrada_usuario = Gtk.Box(
            orientation = Gtk.Orientation.HORIZONTAL,
            spacing = 2
        )
        box.add(box_entrada_usuario)
        box_entrada_usuario.add(self.botao_adicionar)
        box_entrada_usuario.add(self.botao_remover)
        box_entrada_usuario.add(self.entry)

        # conectando comandos
        self.connect('delete-event', self.fechar_janela_clicado)
        self.botao_adicionar.connect(
            'clicked', self.botao_adicionar_clicado
        )
        render_cell_toggle.connect("toggled", self.botao_toggle_ativado)
        self.botao_remover.connect('clicked', self.botao_remover_clicado)
        self.entry.connect('activate', self.botao_adicionar_clicado)
        
    
    def botao_adicionar_clicado(self, widget):
        texto = self.entry.get_text().strip()
        if bool(texto):
            self._liststore.append([False, texto])
        self.entry.set_text('')
    
    def botao_toggle_ativado(self, widget, local):
        self._liststore[local][0] = not self._liststore[local][0]
    
    def botao_remover_clicado(self, widget):
        data, item = self._selecao.get_selected()
        if all((data, item)):
            self._liststore.remove(item)
    
    def fechar_janela_clicado(self, *args):
        self.hide()
        # não remova o comando abaixo. ele faz com que a janela
        # não exclua os seus widgets, e portanto, reabra na próxima vez.
        return True


def abrir_clicado(janela, widget):
    janela.show()


def sair(janela, widget):
    banco = shelve.open('save.pkl')
    tarefas = [list(item) for item in janela._liststore]
    if banco['tarefas'] != tarefas:
        banco['tarefas'] = tarefas
    Gtk.main_quit()


def app_indicator(abrir_clicado_partial, sair_partial):
    indicador = appindicator.Indicator.new(
        'app_da_bandeja', 'icone/checklist.png',
        appindicator.IndicatorCategory.APPLICATION_STATUS
    )
    indicador.set_status(appindicator.IndicatorStatus.ACTIVE)
    
    menu = Gtk.Menu()
    menu_item1 = Gtk.MenuItem(label = 'Abrir')
    menu_item2 = Gtk.MenuItem(label = 'Sair')
    menu.append(menu_item1)
    menu.append(menu_item2)
    menu_item1.connect('activate', abrir_clicado_partial)
    menu_item2.connect('activate', sair_partial)
    menu.show_all()
    indicador.set_menu(menu)
    return indicador


def main():
    janela = TodoList()
    janela.show_all()
    abrir_clicado_partial = partial(abrir_clicado, janela)
    sair_partial = partial(sair, janela)
    indicador = app_indicator(
        abrir_clicado_partial, sair_partial
    )
    with suppress((KeyboardInterrupt, EOFError)):
        Gtk.main()


if __name__ == '__main__':
    main()