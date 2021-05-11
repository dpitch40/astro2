from pygame_gui.elements import UIButton

from astro.util import proportional_rect, convert_prop_x, convert_prop_y, \
    convert_proportional_coordinates

def button_list(manager, button_info,
                pos, button_size, button_spacing=1.2, vertical=True):
    if vertical:
        spacing = convert_prop_y(button_size[1]) * button_spacing
    else:
        spacing = convert_prop_x(button_size[0]) * button_spacing

    x, y = convert_proportional_coordinates(*pos)
    buttons = list()
    button_mapping = dict()
    for text, (function, params) in button_info:
        button = UIButton(relative_rect=proportional_rect((round(x), round(y)), button_size),
                               text=text, manager=manager)
        buttons.append(button)
        button_mapping[button] = (function, params)
        if vertical:
            y += spacing
        else:
            x += spacing

    return button, button_mapping
