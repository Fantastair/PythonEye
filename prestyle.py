import pygame
import pygame.freetype
from fantas import uimanager

r = uimanager.r

dropfile = {
	'size': 26*r,
	'fgcolor': uimanager.WHITE,
}
menubar_menu = {
	'hover_bg': uimanager.BLUE,
	'press_bg': uimanager.BLUE,
	'ban_bg': uimanager.DARKRED2,
	'origin_bg': uimanager.DARKGRAY3,
}
menubar_item = {
	'bd': 1,
	'linebd': 4,
	'sidepad': 3,
	'width': 200,
	'rightpad': 5,
	'leftpad': 30,
	'boxwidth': 206,
	'lineheight': 10,
	'sc': uimanager.DARKGRAY5,
	'normal': uimanager.WHITE,
	'ban': uimanager.DARKGRAY2,
	'hover_bg': uimanager.BLUE,
	'press_bg': uimanager.BLUE,
	'ban_bg': uimanager.DARKGRAY4,
	'origin_bg': uimanager.DARKGRAY4,
}
menubar_text = {
	'size': 15,
	'fgcolor': uimanager.WHITE,
	'style': pygame.freetype.STYLE_STRONG,
}
code_text = {
	'size': 22,
	'fgcolor': uimanager.CODE,
}
linenumber = {
	'size': 22,
	'fgcolor': uimanager.DARKGRAY5,
}
linenumber_hl = {
	'size': 22,
	'fgcolor': uimanager.FAKEWHITE,
}
code_scroll = {
	'barbg': uimanager.DARKGRAY6,
	'hover_bg': uimanager.LIGHTGRAY2,
	'origin_bg': uimanager.LIGHTGRAY1,
}
action_button = {
	'ban_bg': uimanager.DARKRED,
	'hover_bg': uimanager.DARKGRAY5,
	'press_bg': uimanager.DARKGRAY6,
	'origin_bg': uimanager.DARKGRAY2,
}
popbox_text = {
	'size': 18,
	'fgcolor': uimanager.DARKBLUE3,
}
popbox_closebutton = {
	'hover_bg': uimanager.RED,
	'press_bg': uimanager.DARKRED,
	'ban_bg': uimanager.DARKGRAY2,
	'origin_bg': uimanager.DARKBLUE1,
}
popbox_button = {
	'ban_bg': uimanager.DARKBLUE4,
	'hover_bg': uimanager.DARKBLUE6,
	'press_bg': uimanager.DARKBLUE4,
	'origin_bg': uimanager.DARKBLUE2,
}
popbox_inputline = {
	'cursor_size': (2,30),
	'cursor_bg': uimanager.FAKEWHITE,
	'text_pad': 10,
}
message_text = {
	'size': 24,
	'fgcolor': uimanager.DARKBLUE5,
}
message_button = {
	'origin_bg': uimanager.DARKBLUE3,
	'hover_bg': uimanager.DARKBLUE3,
	'press_bg': uimanager.DARKBLUE3,
	'fixed': uimanager.DARKBLUE2,
	'unfixed': uimanager.DARKBLUE3
}
hovermessage_text = {
	'size': 14,
	'fgcolor': uimanager.DARKGRAY1
}
trace_button = {
	'origin_bg': uimanager.BLUE2,
	'hover_bg': uimanager.LIGHTBLUE,
	'press_bg': uimanager.LIGHTBLUE,
	'origin_sc': uimanager.DARKBLUE6,
	'hover_sc': uimanager.YELLOW,
	'press_sc': uimanager.YELLOW,
}
arg_text = {
	'size': 24,
	'fgcolor': uimanager.WHITE
}
arg_name = {
	'size': 26,
	'fgcolor': uimanager.ORANGE,
	'style': pygame.freetype.STYLE_OBLIQUE
}
