from pathlib import Path

import FreeSimpleGUI as Sg

from pocketliftover.application import Config, ConfigException
from pocketliftover.application.options import liftover_categories

chainfile_headers = ['Label', 'Source', 'Destination', 'File']
pattern_headers = ['Label', 'Search Pattern']


def add_liftchain_popup(_chainfile_data=None):
    initial_label = ''
    initial_source_type = None
    initial_destination_type = None
    initial_file_parent = None
    if _chainfile_data is not None:
        initial_label = _chainfile_data['label']
        initial_source_type = _chainfile_data['source_type']
        initial_destination_type = _chainfile_data['destination_type']
        initial_file = Path(_chainfile_data['file'])
        initial_file_parent = initial_file.parent
    popup_layout = [
        [
            Sg.HorizontalSeparator(),
        ], [
            Sg.Text('Label:', size=(15, 1)),
            Sg.Input(key='chainfileLabel', size=(15, 1), default_text=initial_label),
        ], [
            Sg.Text('Liftover Source:', size=(15, 1)),
            Sg.Combo(liftover_categories, key='chainfileSourceType', size=(13, 1), default_value=initial_source_type),
        ], [
            Sg.Text('Liftover Destination:', size=(15, 1)),
            Sg.Combo(liftover_categories, key='chainfileDestinationType', size=(13, 1), default_value=initial_destination_type),
        ], [
            Sg.Text('Chain File', size=(15, 1)),
            Sg.Input(key="chainfileFile"),
            Sg.FileBrowse(initial_folder=initial_file_parent),
        ], [
            Sg.HorizontalSeparator(),
        ], [
            Sg.Checkbox('Save chainfile to local preferences', key='chainfileSaveLocal', default=True)
        ], [
            Sg.Button("Save Chainfile", key="-SAVE-", bind_return_key=True),
            Sg.Button("Cancel", key="-CANCEL-"),
        ]
    ]
    popup_window = Sg.Window('Chainfile Info', popup_layout)
    chainfile_to_return = []
    while True:
        popup_label_event, popup_label_values = popup_window.read()
        if popup_label_event is None or popup_label_event == 'Exit':
            break
        if popup_label_event == '-SAVE-':
            label = popup_label_values['chainfileLabel']
            source_type = popup_label_values['chainfileSourceType']
            destination_type = popup_label_values['chainfileDestinationType']
            file = Path(popup_label_values['chainfileFile'])
            save_local = popup_label_values['chainfileSaveLocal']
            if label.strip() == '':
                Sg.popup_error("Please enter a valid label")
            try:
                chainfile_to_return = Config.save_new_chainfile(label, source_type, destination_type, file, save_local)
                Sg.popup_ok("Chain file saved")
                break
            except ConfigException as e:
                Sg.popup_error(f"Failed to save chainfile: {str(e)}")
    popup_window.close()
    return chainfile_to_return


def add_pattern_popup(_pattern_data=None):
    initial_label = ''
    initial_pattern = ''
    if _pattern_data is not None:
        initial_label = _pattern_data['label']
        initial_pattern = _pattern_data['pattern']
    popup_layout = [
        [
            Sg.HorizontalSeparator(),
        ], [
            Sg.Text('Label:', size=(15, 1)),
            Sg.Input(key='patternLabel', size=(15, 1), default_text=initial_label),
        ], [
            Sg.Text('Search Pattern:', size=(15, 1)),
            Sg.Input(key='patternPattern', size=(40, 1), default_text=initial_pattern),
        ], [
            Sg.Text('NOTE: Please ensure that your pattern uses (?P<chrom>...), (?P<start>...),'),
        ], [
            Sg.Text(' ', size=(4, 1)), Sg.Text('and optionally (?P<end>...) capture groups'),
        ], [
            Sg.HorizontalSeparator(),
        ], [
            Sg.Button("Save Pattern", key="-SAVE-", bind_return_key=True),
            Sg.Button("Cancel", key="-CANCEL-"),
        ]
    ]
    popup_window = Sg.Window('Search Pattern Info', popup_layout)
    pattern_to_return = []
    while True:
        popup_label_event, popup_label_values = popup_window.read()
        if popup_label_event is None or popup_label_event == 'Exit':
            break
        if popup_label_event == '-SAVE-':
            label = popup_label_values['patternLabel']
            pattern = popup_label_values['patternPattern']
            if label.strip() == '':
                Sg.popup_error("Please enter a valid label")
            try:
                pattern_to_return = Config.add_pattern(label, pattern)
                Sg.popup_ok("Search pattern saved")
                break
            except ConfigException as e:
                Sg.popup_error(f"Failed to save search pattern: {str(e)}")
    popup_window.close()
    return pattern_to_return


def preferences_window():
    chainfile_data = []
    for chainfile in Config.get_chainfiles():
        chainfile_object = Config.get_chainfile(chainfile)
        chainfile_data.append([
            chainfile_object.label,
            chainfile_object.source_type,
            chainfile_object.destination_type,
            chainfile_object.file])
    pattern_data = []
    for pattern in Config.get_patterns():
        pattern_object = Config.get_pattern(pattern)
        pattern_data.append([
            pattern_object.label,
            pattern_object.pattern])
    chainfile_tab = [
        [
            Sg.Table(
                values=chainfile_data,
                headings=chainfile_headers,
                auto_size_columns=False,
                col_widths=[10,8,8,34],
                cols_justification=['center', 'center', 'center', 'left'],
                num_rows=5,
                key='chainfilesTable',
                bind_return_key=False,
            )
        ], [
            Sg.Text(' ', size=(19, 1)),
            Sg.Button('Add Chainfile', key='-ADDCHAINFILE-'),
            Sg.Button('Delete Chainfile(s)', key='-DELETECHAINFILE-'),
        ]
    ]
    pattern_tab = [
        [
            Sg.Table(
                values=pattern_data,
                headings=pattern_headers,
                auto_size_columns=False,
                col_widths=[10,50],
                cols_justification=['center', 'left'],
                num_rows=5,
                key='patternsTable',
                bind_return_key=False,
            )
        ], [
            Sg.Text(' ', size=(15, 1)),
            Sg.Button('Add Search Pattern', key='-ADDPATTERN-'),
            Sg.Button('Delete Search Pattern(s)', key='-DELETEPATTERN-'),
        ]
    ]
    layout = [
        [Sg.TabGroup(
            [
                [
                    Sg.Tab('Chainfiles', chainfile_tab),
                    Sg.Tab('Search Patterns', pattern_tab),
                ]
            ]
        )
            ]
    ]

    window = Sg.Window('Preferences', layout)
    while True:
        event, values = window.read()
        if event is None or event == 'Exit':
            break
        if event == '-ADDCHAINFILE-':
            new_chainfile = add_liftchain_popup()
            if new_chainfile is not None:
                chainfile_data.append(new_chainfile)
                window.Element('chainfilesTable').Update(chainfile_data)
        if event == '-DELETECHAINFILE-':
            tmp_new_data = []
            rows_to_remove = values['chainfilesTable']
            if len(rows_to_remove) > 0:
                for i in range(len(chainfile_data)):
                    if i not in rows_to_remove:
                        tmp_new_data.append(chainfile_data[i])
                    else:
                        Config.delete_chainfile(chainfile_data[i][0])
                chainfile_data = tmp_new_data
                window.Element('chainfilesTable').Update(chainfile_data)
        if event == '-ADDPATTERN-':
            new_pattern = add_pattern_popup()
            if new_pattern is not None:
                pattern_data.append(new_pattern)
                window.Element('patternsTable').Update(pattern_data)
        if event == '-DELETEPATTERN-':
            tmp_new_data = []
            rows_to_remove = values['patternsTable']
            if len(rows_to_remove) > 0:
                for i in range(len(pattern_data)):
                    if i not in rows_to_remove:
                        tmp_new_data.append(pattern_data[i])
                    else:
                        Config.delete_pattern(pattern_data[i][0])
                pattern_data = tmp_new_data
                window.Element('patternsTable').Update(pattern_data)
        window.refresh()
    window.close()