import re

import FreeSimpleGUI as Sg

from pocketliftover.application import Config, Lifter, ensure_chr_prefix, toggle_chr_prefix

from .icon import get_gui_icon
from .preferences import preferences_window


def main_window():
    chains = Config.get_chainfiles()
    default_chainfile = Config.get_default_chainfile()
    automatically_copy_to_clipboard = Config.get_automatically_copy_to_clipboard()
    menu = [
        [
            '&File',
            [
                '&Preferences',
                'E&xit',
            ]
        ]
    ]
    layout = [
        [
            Sg.Menu(menu),
        ], [
            Sg.Text('Liftover coordinates between reference genomes'),
        ], [
            Sg.Text('Liftover Chain:'),
            Sg.Combo(chains, key='CHAINFILE', enable_events=True,
                     default_value=default_chainfile.label if default_chainfile else None),
            Sg.Text(f'({default_chainfile.source_type} => {default_chainfile.destination_type})',
                    key='CHAINFILE_TYPES'),
        ], [
            Sg.Text('Text with Coordinate(s):'),
            Sg.Input(key='LIFTOVERTEXT', focus=True), Sg.Button('Liftover', key='-LIFTOVER-')
        ], [
            Sg.Text('Liftover Results:', key='LIFTOVERPARAMS')
        ], [
            Sg.Text(' ', size=(1, 1)), Sg.Text('', key='LIFTOVERRESULTS')
        ], [
            Sg.Button('Copy to Clipboard', key='-CLIPBOARD-'),
            Sg.Checkbox('Automatically copy to clipboard on liftover', default=automatically_copy_to_clipboard,
                        enable_events=True, key='-AUTOCLIPBOARD-'),
        ]
    ]

    window = Sg.Window('PocketLiftover', layout, icon=get_gui_icon(), finalize=True)
    window['LIFTOVERTEXT'].bind('<Return>', '_Enter')
    while True:
        event, values = window.read(timeout=250)
        if event is None or event == 'Exit':
            break
        if event == 'Preferences':
            existing_selection = values['CHAINFILE']
            preferences_window()
            chains = Config.get_chainfiles()
            reset_index = -1
            try:
                reset_index = chains.index(existing_selection)
            except ValueError:
                pass
            window['CHAINFILE'].Update(values=chains)
            if reset_index > -1:
                window['CHAINFILE'].Update(set_to_index=reset_index)
                Config.set_default_chainfile(existing_selection)
            else:
                default_chainfile = None
                window.Element('CHAINFILE_TYPES').Update(f'()')
        if event == 'CHAINFILE':
            Config.set_default_chainfile(values['CHAINFILE'])
            default_chainfile = Config.get_default_chainfile()
            window.Element('CHAINFILE_TYPES').Update(f'({default_chainfile.source_type} => ' +
                                                     f'{default_chainfile.destination_type})')
        if event == '-AUTOCLIPBOARD-':
            Config.set_automatically_copy_to_clipboard(values['-AUTOCLIPBOARD-'])
        if event == '-LIFTOVER-' or event == 'LIFTOVERTEXT' + '_Enter':
            automatically_copy_to_clipboard = values['-AUTOCLIPBOARD-']
            window.Element('LIFTOVERPARAMS').Update("Liftover Results (None):")
            chainfile_label = values['CHAINFILE']
            if chainfile_label is None or chainfile_label == '':
                Sg.popup_error('Please add a valid chainfile', title='No Valid Chainfile')
                continue
            liftover_text = values['LIFTOVERTEXT']
            chainfile = Config.get_chainfile(chainfile_label)
            try:
                lifter = Lifter(chainfile.file)
            except ValueError:
                window.Element('LIFTOVERRESULTS').Update(f"Chain {chainfile.label} is invalid, please delete and " +
                                                         "re-add the correct chainfile")
                continue
            source = None
            ref = None
            chrom = None
            start = None
            end = None
            # Iterate through saved patterns looking for one that can extract genomic coordinates from input text
            for pattern in Config.get_patterns():
                pattern_object = Config.get_pattern(pattern)
                pattern_search = re.compile(pattern_object.pattern, re.IGNORECASE)
                pattern_search_result = pattern_search.search(liftover_text)
                if pattern_search_result is not None:
                    source = pattern
                    try:
                        chrom = pattern_search_result.group('chrom')
                        start = int(pattern_search_result.group('start'))
                        end = pattern_search_result.group('end')
                        if end is not None:
                            end = int(end)
                    except IndexError:
                        pass
            if source is None:
                Sg.popup_error(f"Failed to find coordinates in [{liftover_text}] using any existing patterns")
                continue
            if chrom is None or start is None:
                Sg.popup_error("Pattern must use ?P<chrom>, ?P<start>, and ?P<end> for successful capture")
                continue
            try:
                lifted_beginning = lifter.liftover_coordinate(chrom, start)
            except ValueError:
                # Try liftover again with (or without) chr prefix
                try:
                    lifted_beginning = lifter.liftover_coordinate(toggle_chr_prefix(chrom), start)
                except ValueError:
                    Sg.popup_error(f"Loci range start coordinate {chrom}:{start} failed to liftover",
                                   title="Liftover Error")
                    continue
            lifted_chrom = lifted_beginning[0]
            lifted_start = lifted_beginning[1]
            lifted_end = None
            if end is not None:
                try:
                    lifted_end = lifter.liftover_coordinate(chrom, end)[1]
                except ValueError:
                    # Try liftover again with (or without) chr prefix
                    try:
                        lifted_end = lifter.liftover_coordinate(toggle_chr_prefix(chrom), end)[1]
                    except ValueError:
                        Sg.popup_error(f"Loci range end coordinate {chrom}:{end} failed to liftover",
                                       title="Liftover Error")
                        continue
            # Remove chr prefix from reported hg19 coordinates
            lifted_chrom = ensure_chr_prefix(lifted_chrom, chainfile.destination_type != 'hg19')
            liftover_result = f"{lifted_chrom}:{lifted_start}{f':{lifted_end}' if end else ''}"
            if automatically_copy_to_clipboard:
                Sg.clipboard_set(liftover_result)
            window.Element('LIFTOVERPARAMS').Update(
                f"Liftover Results ({chrom}:{start}{f'-{end}' if end else ''}) " +
                f"({chainfile.source_type} => {chainfile.destination_type} - {source}):")
            window.Element('LIFTOVERRESULTS').Update(liftover_result)
            window.Element('LIFTOVERTEXT').Update('')
        if event == '-CLIPBOARD-':
            Sg.clipboard_set(window.Element('LIFTOVERRESULTS').get())
            window.Element('LIFTOVERTEXT').set_focus(True)
        window.Refresh()
    window.close()
