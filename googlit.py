#!/usr/bin/python3
import configparser, pyperclip, webbrowser, urwid
from importlib.machinery import SourceFileLoader
googler = SourceFileLoader("googler", "/usr/local/bin/googler").load_module()
from xdg.BaseDirectory import *

# Configuration
os.makedirs(os.path.join(xdg_config_home, "googlit"), exist_ok=True)
config_defaults_googlit = {
        'clear_search_on_focus': 'false',
        'language': 'en',
        'max_results': '30',
        'exclude': 'pinterest.com'
        }

config = configparser.ConfigParser()

if os.path.exists(os.path.join(xdg_config_home, 'googlit/config')):
    config.read(os.path.join(xdg_config_home, 'googlit/config'))

    # Check for missing keys
    for i in config_defaults_googlit:
        if not config.has_option('googlit', i):
            config['googlit'][i] = config_defaults_googlit[i]
    with open(os.path.join(xdg_config_home, 'googlit/config'), 'w') as configfile:
        config.write(configfile)
    clear_search_on_focus = config.getboolean('googlit', 'clear_search_on_focus')
    language = config['googlit']['language']
    max_results = int(config['googlit']['max_results'])
    exclude = config['googlit']['exclude']

else:
    config.add_section('googlit')

    for i in config_defaults_googlit:
        config['googlit'][i] = config_defaults_googlit[i]

    with open(os.path.join(xdg_config_home, 'googlit/config'), 'w') as configfile:
        config.write(configfile)

class SearchBox(urwid.Edit):
    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == 'enter':
            PerformSearch(searchbox.base_widget.text)
            if content:
                frame.focus_position = 'body'
        elif key == 'tab':
            if content:
                frame.focus_position = 'body'
        else:
            super().keypress(size, key)
        return key

class ListBoxItem(urwid.Text):
    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == 'enter':
            webbrowser.open(listbox.get_focus()[0].base_widget.text.splitlines()[1], new=2)
        elif key in ('y', 'Y'):
            pyperclip.copy(listbox.get_focus()[0].base_widget.text.splitlines()[1])
        elif key == 'tab':
            frame.focus_position = 'header'
            if clear_search_on_focus:
                searchbox.base_widget.edit_text = ''
        return key

def PerformSearch(term):
    results = []

    repl = googler.GooglerCmd(googler.parse_args(['-n 30', term]))
    repl.fetch()

    for i in repl.results:
        # Assemble the matches string
        matches = ""
        if i.matches:
            for j in i.matches:
                if matches:
                    matches += ', '
                matches += "%s (%s)" % (j.get('phrase'), j.get('offset'))

        results.append(urwid.AttrMap(urwid.LineBox(ListBoxItem([("title", i.title+'\n'), ("url", i.url+'\n'), ("meta", i.metadata.replace(' | ', '\n')+'\n' if i.metadata else ""), ("matches", "Matches: %s" % (matches)+'\n' if matches else ""), ("desc", i.abstract)]), tlcorner='┏', tline='━', lline='┃', trcorner='┓', blcorner='┗', rline='┃', bline='━', brcorner='┛'), 'item_frame', focus_map='item_frame_focus'))

    content[:] = [urwid.AttrMap(w, None, 'default') for w in results]
    listbox.focus_position = 0
    
def exit_on_cq(input):
    if input in ('ctrl q', 'ctrl Q'):
        raise urwid.ExitMainLoop()

palette = [
        ('border', 'dark blue', 'default'),
        ('searchbox', 'black', 'white'),
        ('searchbox_focus', 'white', 'dark blue'),
        ('reveal focus', 'white', 'dark blue', 'standout'),
        ('url', 'brown', 'default'),
        ('title', 'light green', 'default'),
        ('desc', 'default', 'default'),
        ('meta', 'dark cyan', 'default'),
        ('matches', 'dark magenta', 'default'),
        ('item_frame', 'black', 'black'),
        ('item_frame_focus', 'light cyan', 'default')
        ]

searchicon = urwid.Text("\U0001F50D")
searchbox = urwid.AttrMap(SearchBox(""), "searchbox", focus_map="searchbox_focus")
content = urwid.SimpleListWalker([])
listbox = urwid.ListBox(content)

frame = urwid.Frame(listbox, urwid.Pile([urwid.Columns([(3, searchicon), searchbox]), urwid.AttrMap(urwid.Divider('─'), "border")]), focus_part="header")

loop = urwid.MainLoop(urwid.AttrMap(urwid.LineBox(urwid.AttrMap(frame, "default")), "border"), palette, unhandled_input=exit_on_cq)
loop.run()

