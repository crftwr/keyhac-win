import os
import sys
import time
import profile
import ctypes
import fnmatch
import traceback
import winsound

import ckit

import pyauto
from pyauto.pyauto_const import *

import keyhac_hook
import keyhac_clipboard
import keyhac_listwindow
import keyhac_balloon
import keyhac_ini
import keyhac_resource
import keyhac_misc


## @addtogroup keymap
## @{

#--------------------------------------------------------------------

MODKEY_ALT   = 0x00000001
MODKEY_CTRL  = 0x00000002
MODKEY_SHIFT = 0x00000004
MODKEY_WIN   = 0x00000008
MODKEY_USER0 = 0x00000010
MODKEY_USER1 = 0x00000020
MODKEY_USER2 = 0x00000040
MODKEY_USER3 = 0x00000080

MODKEY_ALT_L   = 0x00000100
MODKEY_CTRL_L  = 0x00000200
MODKEY_SHIFT_L = 0x00000400
MODKEY_WIN_L   = 0x00000800
MODKEY_USER0_L = 0x00001000
MODKEY_USER1_L = 0x00002000
MODKEY_USER2_L = 0x00004000
MODKEY_USER3_L = 0x00008000

MODKEY_ALT_R   = 0x00010000
MODKEY_CTRL_R  = 0x00020000
MODKEY_SHIFT_R = 0x00040000
MODKEY_WIN_R   = 0x00080000
MODKEY_USER0_R = 0x00100000
MODKEY_USER1_R = 0x00200000
MODKEY_USER2_R = 0x00400000
MODKEY_USER3_R = 0x00800000

MODKEY_USER_ALL = ( MODKEY_USER0   | MODKEY_USER1   | MODKEY_USER2   | MODKEY_USER3
                  | MODKEY_USER0_L | MODKEY_USER1_L | MODKEY_USER2_L | MODKEY_USER3_L
                  | MODKEY_USER0_R | MODKEY_USER1_R | MODKEY_USER2_R | MODKEY_USER3_R )


def checkModifier( mod1, mod2 ):

    _mod1 = mod1 & 0xff
    _mod2 = mod2 & 0xff
    _mod1_L = (mod1 & 0xff00) >> 8
    _mod2_L = (mod2 & 0xff00) >> 8
    _mod1_R = (mod1 & 0xff0000) >> 16
    _mod2_R = (mod2 & 0xff0000) >> 16

    if _mod1 & ~( _mod2 | _mod2_L | _mod2_R ):
        return False
    if _mod1_L & ~( _mod2 | _mod2_L ):
        return False
    if _mod1_R & ~( _mod2 | _mod2_R ):
        return False
    if _mod2 & ~( _mod1 | _mod1_L | _mod1_R ):
        return False
    if _mod2_L & ~( _mod1 | _mod1_L ):
        return False
    if _mod2_R & ~( _mod1 | _mod1_R ):
        return False
    return True


# mod1 に mod2 が含まれていることを確認する
def hasModifier( mod1, mod2 ):

    _mod1 = mod1 & 0xff
    _mod2 = mod2 & 0xff
    _mod1_L = (mod1 & 0xff00) >> 8
    _mod2_L = (mod2 & 0xff00) >> 8
    _mod1_R = (mod1 & 0xff0000) >> 16
    _mod2_R = (mod2 & 0xff0000) >> 16

    if _mod2 & ( _mod1 | _mod1_L | _mod1_R ):
        return True
    if _mod2_L & ( _mod1 | _mod1_L ):
        return True
    if _mod2_R & ( _mod1 | _mod1_R ):
        return True
    return False


class KeyCondition:

    vk_str_table = {}
    str_vk_table = {}

    vk_str_table_common = {

        VK_A : "A",
        VK_B : "B",
        VK_C : "C",
        VK_D : "D",
        VK_E : "E",
        VK_F : "F",
        VK_G : "G",
        VK_H : "H",
        VK_I : "I",
        VK_J : "J",
        VK_K : "K",
        VK_L : "L",
        VK_M : "M",
        VK_N : "N",
        VK_O : "O",
        VK_P : "P",
        VK_Q : "Q",
        VK_R : "R",
        VK_S : "S",
        VK_T : "T",
        VK_U : "U",
        VK_V : "V",
        VK_W : "W",
        VK_X : "X",
        VK_Y : "Y",
        VK_Z : "Z",

        VK_0 : "0",
        VK_1 : "1",
        VK_2 : "2",
        VK_3 : "3",
        VK_4 : "4",
        VK_5 : "5",
        VK_6 : "6",
        VK_7 : "7",
        VK_8 : "8",
        VK_9 : "9",

        VK_OEM_MINUS  : "Minus",
        VK_OEM_PLUS   : "Plus",
        VK_OEM_COMMA  : "Comma",
        VK_OEM_PERIOD : "Period",

        VK_NUMLOCK  : "NumLock",
        VK_DIVIDE   : "Divide",
        VK_MULTIPLY : "Multiply",
        VK_SUBTRACT : "Subtract",
        VK_ADD      : "Add",
        VK_DECIMAL  : "Decimal",

        VK_NUMPAD0 : "Num0",
        VK_NUMPAD1 : "Num1",
        VK_NUMPAD2 : "Num2",
        VK_NUMPAD3 : "Num3",
        VK_NUMPAD4 : "Num4",
        VK_NUMPAD5 : "Num5",
        VK_NUMPAD6 : "Num6",
        VK_NUMPAD7 : "Num7",
        VK_NUMPAD8 : "Num8",
        VK_NUMPAD9 : "Num9",

        VK_F1  : "F1",
        VK_F2  : "F2",
        VK_F3  : "F3",
        VK_F4  : "F4",
        VK_F5  : "F5",
        VK_F6  : "F6",
        VK_F7  : "F7",
        VK_F8  : "F8",
        VK_F9  : "F9",
        VK_F10 : "F10",
        VK_F11 : "F11",
        VK_F12 : "F12",

        VK_LEFT     : "Left",
        VK_RIGHT    : "Right",
        VK_UP       : "Up",
        VK_DOWN     : "Down",
        VK_SPACE    : "Space",
        VK_TAB      : "Tab",
        VK_BACK     : "Back",
        VK_RETURN   : "Return",
        VK_ESCAPE   : "Escape",
        VK_CAPITAL  : "CapsLock",
        VK_APPS     : "Apps",

        VK_INSERT   : "Insert",
        VK_DELETE   : "Delete",
        VK_HOME     : "Home",
        VK_END      : "End",
        VK_NEXT     : "PageDown",
        VK_PRIOR    : "PageUp",

        VK_MENU     : "Alt",
        VK_LMENU    : "LAlt",
        VK_RMENU    : "RAlt",
        VK_CONTROL  : "Ctrl",
        VK_LCONTROL : "LCtrl",
        VK_RCONTROL : "RCtrl",
        VK_SHIFT    : "Shift",
        VK_LSHIFT   : "LShift",
        VK_RSHIFT   : "RShift",
        VK_LWIN     : "LWin",
        VK_RWIN     : "RWin",

        VK_SNAPSHOT : "PrintScreen",
        VK_SCROLL   : "ScrollLock",
        VK_PAUSE    : "Pause",

        VK_LBUTTON : "LBUTTON", # mouse button
        VK_RBUTTON : "RBUTTON", # mouse button
        VK_MBUTTON : "MBUTTON", # mouse button
    }

    vk_str_table_std = {
        VK_OEM_1 : "Semicolon",
        VK_OEM_2 : "Slash",
        VK_OEM_3 : "BackQuote",
        VK_OEM_4 : "OpenBracket",
        VK_OEM_5 : "BackSlash",
        VK_OEM_6 : "CloseBracket",
        VK_OEM_7 : "Quote",
    }

    vk_str_table_jpn = {
        VK_OEM_1    : "Colon",
        VK_OEM_2    : "Slash",
        VK_OEM_3    : "Atmark",
        VK_OEM_4    : "OpenBracket",
        VK_OEM_5    : "Yen",
        VK_OEM_6    : "CloseBracket",
        VK_OEM_7    : "Caret",
        VK_OEM_102  : "BackSlash",
    }

    str_vk_table_common = {

        "A" : VK_A,
        "B" : VK_B,
        "C" : VK_C,
        "D" : VK_D,
        "E" : VK_E,
        "F" : VK_F,
        "G" : VK_G,
        "H" : VK_H,
        "I" : VK_I,
        "J" : VK_J,
        "K" : VK_K,
        "L" : VK_L,
        "M" : VK_M,
        "N" : VK_N,
        "O" : VK_O,
        "P" : VK_P,
        "Q" : VK_Q,
        "R" : VK_R,
        "S" : VK_S,
        "T" : VK_T,
        "U" : VK_U,
        "V" : VK_V,
        "W" : VK_W,
        "X" : VK_X,
        "Y" : VK_Y,
        "Z" : VK_Z,

        "0" : VK_0,
        "1" : VK_1,
        "2" : VK_2,
        "3" : VK_3,
        "4" : VK_4,
        "5" : VK_5,
        "6" : VK_6,
        "7" : VK_7,
        "8" : VK_8,
        "9" : VK_9,

        "MINUS"  : VK_OEM_MINUS,
        "PLUS"   : VK_OEM_PLUS,
        "COMMA"  : VK_OEM_COMMA,
        "PERIOD" : VK_OEM_PERIOD,

        "NUMLOCK"  : VK_NUMLOCK,
        "DIVIDE"   : VK_DIVIDE,
        "MULTIPLY" : VK_MULTIPLY,
        "SUBTRACT" : VK_SUBTRACT,
        "ADD"      : VK_ADD,
        "DECIMAL"  : VK_DECIMAL,

        "NUM0" : VK_NUMPAD0,
        "NUM1" : VK_NUMPAD1,
        "NUM2" : VK_NUMPAD2,
        "NUM3" : VK_NUMPAD3,
        "NUM4" : VK_NUMPAD4,
        "NUM5" : VK_NUMPAD5,
        "NUM6" : VK_NUMPAD6,
        "NUM7" : VK_NUMPAD7,
        "NUM8" : VK_NUMPAD8,
        "NUM9" : VK_NUMPAD9,

        "F1"  : VK_F1,
        "F2"  : VK_F2,
        "F3"  : VK_F3,
        "F4"  : VK_F4,
        "F5"  : VK_F5,
        "F6"  : VK_F6,
        "F7"  : VK_F7,
        "F8"  : VK_F8,
        "F9"  : VK_F9,
        "F10" : VK_F10,
        "F11" : VK_F11,
        "F12" : VK_F12,

        "LEFT"     : VK_LEFT  ,
        "RIGHT"    : VK_RIGHT ,
        "UP"       : VK_UP    ,
        "DOWN"     : VK_DOWN  ,
        "SPACE"    : VK_SPACE ,
        "TAB"      : VK_TAB   ,
        "BACK"     : VK_BACK  ,
        "RETURN"   : VK_RETURN,
        "ENTER"    : VK_RETURN,
        "ESCAPE"   : VK_ESCAPE,
        "ESC"      : VK_ESCAPE,
        "CAPSLOCK" : VK_CAPITAL,
        "CAPS"     : VK_CAPITAL,
        "CAPITAL"  : VK_CAPITAL,
        "APPS"     : VK_APPS,

        "INSERT"   : VK_INSERT,
        "DELETE"   : VK_DELETE,
        "HOME"     : VK_HOME,
        "END"      : VK_END,
        "PAGEDOWN" : VK_NEXT,
        "PAGEUP"   : VK_PRIOR,

        "ALT"  : VK_MENU ,
        "LALT" : VK_LMENU,
        "RALT" : VK_RMENU,
        "CTRL"  : VK_CONTROL ,
        "LCTRL" : VK_LCONTROL,
        "RCTRL" : VK_RCONTROL,
        "SHIFT"  : VK_SHIFT ,
        "LSHIFT" : VK_LSHIFT,
        "RSHIFT" : VK_RSHIFT,
        "LWIN" : VK_LWIN,
        "RWIN" : VK_RWIN,

        "PRINTSCREEN" : VK_SNAPSHOT,
        "SCROLLLOCK"  : VK_SCROLL,
        "PAUSE"       : VK_PAUSE,
        
        "LBUTTON" : VK_LBUTTON, # mouse button
        "RBUTTON" : VK_RBUTTON, # mouse button
        "MBUTTON" : VK_MBUTTON, # mouse button
    }

    str_vk_table_std = {

        "SEMICOLON"     : VK_OEM_1,
        "COLON"         : VK_OEM_1,
        "SLASH"         : VK_OEM_2,
        "BACKQUOTE"     : VK_OEM_3,
        "TILDE"         : VK_OEM_3,
        "OPENBRACKET"   : VK_OEM_4,
        "BACKSLASH"     : VK_OEM_5,
        "YEN"           : VK_OEM_5,
        "CLOSEBRACKET"  : VK_OEM_6,
        "QUOTE"         : VK_OEM_7,
        "DOUBLEQUOTE"   : VK_OEM_7,
        "UNDERSCORE"    : VK_OEM_MINUS,
        "ASTERISK"      : VK_8,
        "ATMARK"        : VK_2,
        "CARET"         : VK_6,
    }

    str_vk_table_jpn = {

        "SEMICOLON"     : VK_OEM_PLUS,
        "COLON"         : VK_OEM_1,
        "SLASH"         : VK_OEM_2,
        "BACKQUOTE"     : VK_OEM_3,
        "TILDE"         : VK_OEM_7,
        "OPENBRACKET"   : VK_OEM_4,
        "BACKSLASH"     : VK_OEM_102,
        "YEN"           : VK_OEM_5,
        "CLOSEBRACKET"  : VK_OEM_6,
        "QUOTE"         : VK_7,
        "DOUBLEQUOTE"   : VK_2,
        "UNDERSCORE"    : VK_OEM_102,
        "ASTERISK"      : VK_OEM_1,
        "ATMARK"        : VK_OEM_3,
        "CARET"         : VK_OEM_7,
    }

    str_mod_table = {

        "ALT"   :  MODKEY_ALT,
        "CTRL"  :  MODKEY_CTRL,
        "SHIFT" :  MODKEY_SHIFT,
        "WIN"   :  MODKEY_WIN,
        "USER0" :  MODKEY_USER0,
        "USER1" :  MODKEY_USER1,
        "USER2" :  MODKEY_USER2,
        "USER3" :  MODKEY_USER3,

        "LALT"   :  MODKEY_ALT_L,
        "LCTRL"  :  MODKEY_CTRL_L,
        "LSHIFT" :  MODKEY_SHIFT_L,
        "LWIN"   :  MODKEY_WIN_L,
        "LUSER0" :  MODKEY_USER0_L,
        "LUSER1" :  MODKEY_USER1_L,
        "LUSER2" :  MODKEY_USER2_L,
        "LUSER3" :  MODKEY_USER3_L,

        "RALT"   :  MODKEY_ALT_R,
        "RCTRL"  :  MODKEY_CTRL_R,
        "RSHIFT" :  MODKEY_SHIFT_R,
        "RWIN"   :  MODKEY_WIN_R,
        "RUSER0" :  MODKEY_USER0_R,
        "RUSER1" :  MODKEY_USER1_R,
        "RUSER2" :  MODKEY_USER2_R,
        "RUSER3" :  MODKEY_USER3_R,

        "A" :  MODKEY_ALT,
        "C" :  MODKEY_CTRL,
        "S" :  MODKEY_SHIFT,
        "W" :  MODKEY_WIN,
        "U0" : MODKEY_USER0,
        "U1" : MODKEY_USER1,
        "U2" : MODKEY_USER2,
        "U3" : MODKEY_USER3,

        "LA" :  MODKEY_ALT_L,
        "LC" :  MODKEY_CTRL_L,
        "LS" :  MODKEY_SHIFT_L,
        "LW" :  MODKEY_WIN_L,
        "LU0" : MODKEY_USER0_L,
        "LU1" : MODKEY_USER1_L,
        "LU2" : MODKEY_USER2_L,
        "LU3" : MODKEY_USER3_L,

        "RA" :  MODKEY_ALT_R,
        "RC" :  MODKEY_CTRL_R,
        "RS" :  MODKEY_SHIFT_R,
        "RW" :  MODKEY_WIN_R,
        "RU0" : MODKEY_USER0_R,
        "RU1" : MODKEY_USER1_R,
        "RU2" : MODKEY_USER2_R,
        "RU3" : MODKEY_USER3_R,
    }

    def __init__( self, vk, mod=0, up=False, oneshot=False ):
        if type(vk)==str and len(vk)==1 : vk=ord(vk)
        self.vk = vk
        self.mod = mod
        self.up = up
        self.oneshot = oneshot

    def __hash__(self):
        return self.vk

    def __eq__(self,other):
        if self.vk!=other.vk : return False
        if not checkModifier( self.mod, other.mod ) : return False
        if self.up!=other.up : return False
        if self.oneshot!=other.oneshot : return False
        return True

    def __str__(self):

        s = ""

        if self.oneshot:
            s += "O-"
        elif self.up:
            s += "U-"
        else:
            s += "D-"

        if self.mod & MODKEY_ALT : s += "A-"
        elif self.mod & MODKEY_ALT_L : s += "LA-"
        elif self.mod & MODKEY_ALT_R : s += "RA-"

        if self.mod & MODKEY_CTRL : s += "C-"
        elif self.mod & MODKEY_CTRL_L : s += "LC-"
        elif self.mod & MODKEY_CTRL_R : s += "RC-"

        if self.mod & MODKEY_SHIFT : s += "S-"
        elif self.mod & MODKEY_SHIFT_L : s += "LS-"
        elif self.mod & MODKEY_SHIFT_R : s += "RS-"

        if self.mod & MODKEY_WIN : s += "W-"
        elif self.mod & MODKEY_WIN_L : s += "LW-"
        elif self.mod & MODKEY_WIN_R : s += "RW-"

        if self.mod & MODKEY_USER0 : s += "U0-"
        elif self.mod & MODKEY_USER0_L : s += "LU0-"
        elif self.mod & MODKEY_USER0_R : s += "RU0-"

        if self.mod & MODKEY_USER1 : s += "U1-"
        elif self.mod & MODKEY_USER1_L : s += "LU1-"
        elif self.mod & MODKEY_USER1_R : s += "RU1-"

        if self.mod & MODKEY_USER2 : s += "U2-"
        elif self.mod & MODKEY_USER2_L : s += "LU2-"
        elif self.mod & MODKEY_USER2_R : s += "RU2-"

        if self.mod & MODKEY_USER3 : s += "U3-"
        elif self.mod & MODKEY_USER3_L : s += "LU3-"
        elif self.mod & MODKEY_USER3_R : s += "RU3-"

        s += KeyCondition.vkToStr(self.vk)

        return s

    @staticmethod
    def fromString(s):

        s = s.upper()

        vk = None
        mod=0
        up=False
        oneshot=False

        token_list = s.split("-")

        for token in token_list[:-1]:

            token = token.strip()

            try:
                mod |= KeyCondition.strToMod(token)
            except ValueError:
                if token=="O":
                    oneshot = True
                elif token=="D":
                    up = False
                elif token=="U":
                    up = True
                else:
                    raise ValueError

        token = token_list[-1].strip()

        vk = KeyCondition.strToVk(token)

        return KeyCondition( vk, mod, up=up, oneshot=oneshot )

    @staticmethod
    def initTables():

        keyboard_type = ctypes.windll.user32.GetKeyboardType(0)

        KeyCondition.str_vk_table = KeyCondition.str_vk_table_common
        KeyCondition.vk_str_table = KeyCondition.vk_str_table_common

        if keyboard_type==7:
            KeyCondition.str_vk_table.update(KeyCondition.str_vk_table_jpn)
            KeyCondition.vk_str_table.update(KeyCondition.vk_str_table_jpn)
        else:
            KeyCondition.str_vk_table.update(KeyCondition.str_vk_table_std)
            KeyCondition.vk_str_table.update(KeyCondition.vk_str_table_std)

    @staticmethod
    def strToVk(name):
        try:
            vk = KeyCondition.str_vk_table[name.upper()]
        except KeyError:
            try:
                vk = int(name.strip("()"))
            except:
                raise ValueError
        return vk

    @staticmethod
    def vkToStr(vk):
        try:
            name = KeyCondition.vk_str_table[vk]
        except KeyError:
            name = "(%d)" % vk
        return name

    @staticmethod
    def strToMod( name, force_LR=False ):
        try:
            mod = KeyCondition.str_mod_table[ name.upper() ]
        except KeyError:
            raise ValueError
        if force_LR and (mod & 0xff):
            mod <<= 8
        return mod


## Keymap.defineWindowKeymap や Keymap.defineMultiStrokeKeymap によって作られる ウインドウ条件ごとのキーマップ定義
class WindowKeymap:

    def __init__( self, exe_name=None, class_name=None, window_text=None, check_func=None, help_string=None ):
        self.exe_name = exe_name
        self.class_name = class_name
        self.window_text = window_text
        self.check_func = check_func
        self.help_string = help_string

        ## キーマップの適用直前に呼ばれるコールバック関数
        #  
        #  applying_func に設定された関数は、キーマップが適用される直前に呼び出され、
        #  必要に応じて、キーマップの内容を変更することができます。
        #  関数には、引数や返値はありません。
        #
        self.applying_func = None
        
        self.keymap = {}

    def check( self, wnd ):
        if self.exe_name     and ( not wnd or not fnmatch.fnmatch( wnd.getProcessName(), self.exe_name ) ) : return False
        if self.class_name   and ( not wnd or not fnmatch.fnmatch( wnd.getClassName(), self.class_name ) ) : return False
        if self.window_text  and ( not wnd or not fnmatch.fnmatch( wnd.getText(), self.window_text ) ) : return False
        if self.check_func   and ( not wnd or not self.check_func(wnd) ) : return False
        return True

    def helpString(self):
        return self.help_string

    def __setitem__( self, name, value ):

        try:
            key_cond = KeyCondition.fromString(name)
        except ValueError:
            print( ckit.strings["error_invalid_key_expression"], name )
            return

        self.keymap[key_cond] = value

    def __getitem__( self, name ):

        try:
            key_cond = KeyCondition.fromString(name)
        except ValueError:
            print( ckit.strings["error_invalid_key_expression"], name )
            return

        return self.keymap[key_cond]

    def __delitem__( self, name ):
        try:
            key_cond = KeyCondition.fromString(name)
        except ValueError:
            print( ckit.strings["error_invalid_key_expression"], name )
            return

        del self.keymap[key_cond]


## キーの置き換えや任意の処理の実行を行うクラス
#
#  keyhacの主な機能を実現しているクラスです。\n\n
#
#  設定ファイル config.py の configure に渡される keyhac 引数は、Keymap クラスのオブジェクトです。
#
class Keymap(ckit.Window):

    def __init__( self, config_filename, debug, profile ):

        ckit.Window.__init__(
            self,
            x = 0,
            y = 0,
            width = 1,
            height = 1,
            title_bar = True,
            title = "Keyhac keymap",
            show = False,
            endsession_handler = self._onEndSession,
            )

        self.config_filename = config_filename  # config.py のファイルパス
        self.editor = ""                        # config.pyを編集するためのテキストエディタ
        self.quote_mark = ""                    # クリップボードから貼り付けるときの引用記号
        self.cblisters = []                     # クリップボードの履歴リストを表示するときのメニュー生成関数リスト
        self.debug = False                      # デバッグモード
        self.profile = profile                  # プロファイルモード
        self.window_keymap_list = []            # WindowKeymapオブジェクトのリスト
        self.multi_stroke_keymap = None         # マルチストローク用のWindowKeymapオブジェクト
        self.current_map = {}                   # 現在フォーカスされているウインドウで有効なキーマップ
        self.vk_mod_map = {}                    # モディファイアキーの仮想キーコードとビットのテーブル
        self.vk_vk_map = {}                     # キーの置き換えテーブル
        self.wnd = None                         # 現在フォーカスされているウインドウオブジェクト
        self.modifier = 0                       # 押されているモディファイアキーのビットの組み合わせ
        self.oneshot_candidate = None           # ワンショットモディファイアの候補 (最後にDownされたキー)
        self.cancel_oneshot = False             # マウス操作でOneshotモディファイアをキャンセル
        self.input_seq = []                     # 仮想のキー入力シーケンス ( beginInput ～ endInput で使用 )
        self.virtual_modifier = 0               # 仮想のモディファイアキー状態 ( beginInput ～ endInput で使用 )
        self.record_status = None               # キーボードマクロの状態
        self.record_seq = None                  # キーボードマクロのシーケンス
        self.hook_call_list = []                # フック内呼び出し関数のリスト
        
        self.font_name = "MS Gothic"
        self.font_size = 12

        self.console_window = None
        self.list_window = None

        self.sanity_check_state = None
        self.sanity_check_count = 0

        # TRU のときも Input.send() を呼ぶかどうかのデバッグ用フラグ。
        # クリップボード履歴リストの表示に DelayedCall を使うようにしたら
        # モディファイアキーが押しっぱなしになる現象が起きなくなったので、
        # 廃止できそう。
        # これを有効にすると、Win8 でAlt-TAB などが効かなくなる。
        self.send_input_on_tru = keyhac_ini.getint( "DEBUG", "send_input_on_tru", 0 )


        ## サブスレッドからメインスレッド中の処理を呼び出すためのSyncCallオブジェクト
        self.synccall = ckit.SyncCall()

        self.setTimer( self._onTimer, 10 )
        self.setTimer( self._onTimerCheckSanity, 100 )

        self.clipboard_history = keyhac_clipboard.cblister_ClipboardHistory( self, debug=debug )

        self.balloon = None
        self.balloon_name = ""
        self.balloon_timer = None

        self.enableHook(True)
        self.enableDebug(debug)

    def destroy(self):

        if self.balloon:
            self.balloon.destroy()
            self.balloon = None

        self.clipboard_history.destroy()
        self._releaseModifierAll()
        self.enableHook(False)

        ckit.Window.destroy(self)

    def quit(self):
        self.cancelListWindow()
        ckit.Window.quit(self)

    def setConsoleWindow( self, console_window ):
        self.console_window = console_window

    def _onEndSession(self):
        self.clipboard_history.save()
        keyhac_ini.write()

    def _onTimer(self):
        ckit.JobQueue.checkAll()
        self.synccall.check()

    def _onTimerCheckSanity(self):
        self.checkSanity()
        self.clipboard_history.checkSanity()

    ## キーボードとマウスのフックを有効／無効にする
    #
    #  @param self   -
    #  @param enable 有効にするか、無効にするか
    #
    def enableHook( self, enable ):
        self.hook_enabled = enable
        if self.hook_enabled:
            keyhac_hook.hook.keydown = self._hook_onKeyDown
            keyhac_hook.hook.keyup = self._hook_onKeyUp
            keyhac_hook.hook.mousedown = self._hook_onMouseDown
            keyhac_hook.hook.mouseup = self._hook_onMouseUp
            keyhac_hook.hook.mousewheel = self._hook_onMouseWheel
            keyhac_hook.hook.mousehorizontalwheel = self._hook_onMouseHorizontalWheel
        else:
            keyhac_hook.hook.keydown = None
            keyhac_hook.hook.keyup = None
            keyhac_hook.hook.mousedown = None
            keyhac_hook.hook.mouseup = None
            keyhac_hook.hook.mousewheel = None
            keyhac_hook.hook.mousehorizontalwheel = None

    def enableDebug( self, enable ):
        self.debug = enable
        self.clipboard_history.enableDebug(enable)
        pyauto.setDebug(enable)

    ## フォントを設定する
    #
    #  @param self  -
    #  @param name  フォント名
    #  @param size  フォントサイズ
    #
    def setFont( self, name, size ):

        self.font_name = name
        self.font_size = size

        self.console_window.setFont( name, size )

    ## テーマを設定する
    #
    #  @param self  -
    #  @param name  テーマ名
    #
    #  引数 name には、theme ディレクトリ以下のディレクトリ名を与えます。
    #
    def setTheme( self, name ):
        ckit.setTheme( name, {} )
        self.console_window.reloadTheme()

    def _releaseModifierAll(self):
        input_seq = []
        for vk_mod in self.vk_mod_map.items():
            if vk_mod[1] & MODKEY_USER_ALL:
                continue
            input_seq.append( pyauto.KeyUp(vk_mod[0]) )
        pyauto.Input.send(input_seq)

    ## 設定を読み込む
    #
    #  キーマップやモディファイアキーの定義などをリセットした上で、config.py を再読み込みします。
    #
    def configure(self):

        self._releaseModifierAll()

        ckit.Keymap.init()

        KeyCondition.initTables()

        self.window_keymap_list = []
        self.current_map = {}
        self.vk_mod_map = {}
        self.vk_vk_map = {}
        self.modifier = 0

        self.vk_mod_map[VK_LSHIFT   ] = MODKEY_SHIFT_L
        self.vk_mod_map[VK_RSHIFT   ] = MODKEY_SHIFT_R
        self.vk_mod_map[VK_LCONTROL ] = MODKEY_CTRL_L
        self.vk_mod_map[VK_RCONTROL ] = MODKEY_CTRL_R
        self.vk_mod_map[VK_LMENU    ] = MODKEY_ALT_L
        self.vk_mod_map[VK_RMENU    ] = MODKEY_ALT_R
        self.vk_mod_map[VK_LWIN     ] = MODKEY_WIN_L
        self.vk_mod_map[VK_RWIN     ] = MODKEY_WIN_R

        self.editor = "notepad.exe"
        self.quote_mark = "> "
        self.cblisters = [
            ( ckit.strings["title_clipboard"], self.clipboard_history )
            ]

        ckit.CronTable.defaultCronTable().cancel()
        ckit.CronTable.defaultCronTable().clear()

        ckit.reloadConfigScript( self.config_filename )
        ckit.callConfigFunc("configure",self)

        self._updateFocusWindow()

    ## テキストファイルを編集する
    #
    #  @param self  -
    #  @param filename  ファイル名
    #
    def editTextFile( self, filename ):
        if callable(self.editor):
            self.editor(filename)
        else:
            pyauto.shellExecute( None, self.editor, '"%s"' % filename, "" )

    ## config.py を編集する
    #
    #  @param self  -
    #
    def editConfigFile(self):
        self.editTextFile(self.config_filename)

    def startup(self):
        self.clipboard_history.load()
        print( keyhac_resource.startupString() )

    def _hasKeyAction( self, key ):
        return key in self.current_map

    def _keyAction( self, key ):

        if self.debug : print( "IN  :", key )

        try:
            try:
                handler = self.current_map[key]
            except KeyError:
                if self.multi_stroke_keymap and not key.up and not key.oneshot and not key.vk in self.vk_mod_map:
                    winsound.MessageBeep()
                    return True
                else:
                    return False
        finally:
            if not key.up and not key.oneshot and not key.vk in self.vk_mod_map:
                self.leaveMultiStroke()

        if callable(handler):

            self._cancelOneshotWinAlt()

            handler()

        elif isinstance(handler,WindowKeymap):

            self._cancelOneshotWinAlt()

            self.enterMultiStroke(handler)

        else:
            if type(handler)!=list and type(handler)!=tuple:
                handler = [handler]

            self.beginInput()

            for item in handler:

                if type(item)==str:
                    self.setInput_FromString(item)
                else:
                    raise TypeError;

            self.endInput()

        return True

    def _debugKeyState( self, vk ):

        state = pyauto.Input.getKeyboardState()
        print( "getKeyboardState(%d): 0x%x" % ( vk, ord(state[vk]) ) )

        state = pyauto.Input.getKeyState(vk)
        print( "getKeyState(%d):      0x%x" % ( vk, state ) )

        state = pyauto.Input.getAsyncKeyState(vk)
        print( "getAsyncKeyState(%d): 0x%x" % ( vk, state ) )

    def _recordKey( self, vk, up ):
        if self.record_status=="recording":
            if len(self.record_seq)>=1000:
                print( ckit.strings["error_macro_too_long"] )
                return
            self.record_seq.append( ( vk, up ) )

    def _onKeyDown( self, vk ):

        if vk==0:
            for func in self.hook_call_list:
                func()
            self.hook_call_list = []
            return True

        self._updateFocusWindow()

        self._fixFunnyModifierState()

        self._recordKey( vk, False )

        try:
            vk = self.vk_vk_map[vk]
            replaced = True
        except KeyError:
            replaced = False

        #self._debugKeyState(vk)

        self.oneshot_candidate = vk

        try:
            old_modifier = self.modifier
            if vk in self.vk_mod_map:
                self.modifier |= self.vk_mod_map[vk]
                if self.vk_mod_map[vk] & MODKEY_USER_ALL:
                    key = KeyCondition( vk, old_modifier, up=False )
                    self._keyAction(key)
                    return True

            key = KeyCondition( vk, old_modifier, up=False )

            if self._keyAction(key):
                return True
            elif replaced:
                key_seq = [ pyauto.KeyDown(vk) ]
                if self.debug : print( "REP :", key_seq )
                pyauto.Input.send(key_seq)
                return True
            else:
                if self.send_input_on_tru:
                    # 一部の環境でモディファイアが押しっぱなしになってしまう現象の回避テスト
                    # TRU でも Input.send すると問題が起きない
                    key_seq = [ pyauto.KeyDown(vk) ]
                    if self.debug : print( "TRU :", key_seq )
                    pyauto.Input.send(key_seq)
                    return True
                else:
                    if self.debug : print( "TRU :", key )
                    return False

        except Exception as e:
            print( ckit.strings["error_unexpected"], "_onKeyDown" )
            print( e )
            traceback.print_exc()

    def _onKeyUp( self, vk ):

        self._updateFocusWindow()

        self._fixFunnyModifierState()

        self._recordKey( vk, True )

        try:
            vk = self.vk_vk_map[vk]
            replaced = True
        except KeyError:
            replaced = False

        #self._debugKeyState(vk)

        oneshot = ( vk==self.oneshot_candidate and not self.cancel_oneshot )
        self.oneshot_candidate = None
        self.cancel_oneshot = False

        try: # for error
            try: # for oneshot
                if vk in self.vk_mod_map:

                    self.modifier &= ~self.vk_mod_map[vk]

                    if self.vk_mod_map[vk] & MODKEY_USER_ALL:
                        key = KeyCondition( vk, self.modifier, up=True )
                        self._keyAction(key)
                        return True

                key = KeyCondition( vk, self.modifier, up=True )

                if oneshot:
                    oneshot_key = KeyCondition( vk, self.modifier, up=False, oneshot=True )

                if self._keyAction(key):
                    return True
                elif replaced or ( oneshot and self._hasKeyAction(oneshot_key) ):
                    key_seq = [ pyauto.KeyUp(vk) ]
                    if self.debug : print( "REP :", key_seq )
                    pyauto.Input.send(key_seq)
                    return True
                else:
                    if self.send_input_on_tru:
                        # 一部の環境でモディファイアが押しっぱなしになってしまう現象の回避テスト
                        # TRU でも Input.send すると問題が起きない
                        key_seq = [ pyauto.KeyUp(vk) ]
                        if self.debug : print( "TRU :", key_seq )
                        pyauto.Input.send(key_seq)
                        return True
                    else:
                        if self.debug : print( "TRU :", key )
                        return False

            finally:
                # ワンショットモディファイア は Up を処理した後に実行する
                # モディファイアキーの Up -> Down を偽装しなくてよいように。
                # Up を処理する前に Up -> Down を偽装すると、他のウインドウで
                # モディファイアが押しっぱなしになるなどの問題があるようだ。
                if oneshot:
                    key = KeyCondition( vk, self.modifier, up=False, oneshot=True )
                    self._keyAction(key)

        except Exception as e:
            print( ckit.strings["error_unexpected"], "_onKeyUp" )
            print( e )
            traceback.print_exc()

    def enterMultiStroke( self, keymap ):

        self.multi_stroke_keymap = keymap
        self.updateKeymap()

        help_string = self.multi_stroke_keymap.helpString()
        if help_string:
            self.popBalloon( "MultiStroke", help_string )

    def leaveMultiStroke(self):

        if self.multi_stroke_keymap:
            self.multi_stroke_keymap = None
            self.updateKeymap()

            self.closeBalloon( "MultiStroke" )


    ## 現在有効なキーマップを再構築する
    #
    #  現在キーボードフォーカスを持っているウインドウに従って、有効なキー割り当ての辞書を再構築します。\n
    #  通常は、キーボードフォーカスが変化したときに、このメソッドが自動的に呼ばれるため、自分で明示的にこのメソッドを呼ぶ必要はありませんが、
    #  defineWindowKeymap などで定義した WindowKeymap オブジェクトのキー割り当て内容を動的に変更するような場合は、
    #  このメソッドを明示的に呼ぶことで即時にキー割り当ての辞書を再構築を実行することができます。
    #
    def updateKeymap(self):

        self.current_map = {}

        if self.multi_stroke_keymap:
            if self.multi_stroke_keymap.applying_func:
                self.multi_stroke_keymap.applying_func()
            self.current_map.update(self.multi_stroke_keymap.keymap)
        else:
            for window_keymap in self.window_keymap_list:
                if window_keymap.check(self.wnd):
                    if window_keymap.applying_func:
                        window_keymap.applying_func()
                    self.current_map.update(window_keymap.keymap)


    def _focusChanged( self, wnd ):
        try:
            if self.debug:

                if wnd:
                    print( "" )
                    print( "Window : exe   : %s" % wnd.getProcessName() )
                    print( "       : class : %s" % wnd.getClassName() )
                    print( "       : text  : %s" % wnd.getText() )
                    print( "" )
                else:
                    print( "Window : None" )
            
            self.wnd = wnd
            self.updateKeymap()

        except Exception as e:
            print( ckit.strings["error_unexpected"], "_focusChanged" )
            print( e )
            print( "      : %s : %s : %s" % ( wnd.getProcessName(), wnd.getClassName(), wnd.getText() ) )
            traceback.print_exc()

    def _hook_onKeyDown( self, vk, scan ):

        # キーフック強制解除検出カウンタをリセット
        self.sanity_check_count = 0

        if self.profile:
            result = [None]
            profile.runctx( "result[0] = self._onKeyDown(vk)", globals(), locals() )
            return result[0]
        else:
            return self._onKeyDown(vk)

    def _hook_onKeyUp( self, vk, scan ):

        # キーフック強制解除検出カウンタをリセット
        self.sanity_check_count = 0

        if self.profile:
            result = [None]
            profile.runctx( "result[0] = self._onKeyUp(vk)", globals(), locals() )
            return result[0]
        else:
            return self._onKeyUp(vk)

    def _hook_onMouseDown( self, x, y, vk ):

        # マウスボタンを操作するとワンショットモディファイアはキャンセルする
        if self.oneshot_candidate:
            self.cancel_oneshot = True

    def _hook_onMouseUp( self, x, y, vk ):
        pass

    def _hook_onMouseWheel( self, x, y, wheel ):

        # マウスホイールを操作するとワンショットモディファイアはキャンセルする
        if self.oneshot_candidate:
            self.cancel_oneshot = True

    def _hook_onMouseHorizontalWheel( self, x, y, wheel ):

        # マウスホイールを操作するとワンショットモディファイアはキャンセルする
        if self.oneshot_candidate:
            self.cancel_oneshot = True

    ## キーの単純な置き換えを指示する
    #
    #  @param self -
    #  @param src  置き換え前のキー
    #  @param dst  置き換え後のキー
    #
    #  引数 src で指定されたキー入力を、引数 dst で指定されたキーの入力として扱うよう指示します。\n
    #  この置き換え処理は、Keyhac のキー処理の、もっとも早い段階で行われますので、
    #  キーに機能を割り当てる際は、この置き換え後のキーで記述する必要があります。\n\n
    #
    #  src と dst には、"Space" や "Left" のような文字列形式の識別子か、仮想キーコードを数値で渡します。
    #
    def replaceKey( self, src, dst ):
        try:
            if type(src)==str:
                src = KeyCondition.strToVk(src)
        except:
            print( ckit.strings["error_invalid_expression_for_argument"] % ("src",), src )
            return

        try:
            if type(dst)==str:
                dst = KeyCondition.strToVk(dst)
        except:
            print( ckit.strings["error_invalid_expression_for_argument"] % ("dst",), dst )
            return

        self.vk_vk_map[src] = dst

    ## ユーザモディファイアキーを定義する
    #
    #  @param self -
    #  @param vk   モディファイアとして使用するキー
    #  @param mod  割り当てるモディファイアキー
    #
    #  引数 vk で指定されたキーを、mod で指定されたモディファイアキーとして扱うよう指示します。\n\n
    #
    #  モディファイアキーとは、Shift や Ctrl のように、同時に押しておくことで、
    #  キー入力に別の意味を持たせるためのキーのことです。\n\n
    #
    #  vk には、"Space" や "Left" のような文字列形式の識別子か、仮想キーコードを数値で渡します。\n
    #  mod には、"User0" や "U0" のような文字列形式の識別子を渡します。
    #
    def defineModifier( self, vk, mod ):

        try:
            vk_org = vk
            if type(vk)==str:
                vk = KeyCondition.strToVk(vk)
        except:
            print( ckit.strings["error_invalid_expression_for_argument"] % ("vk",), vk )
            return

        try:
            if type(mod)==str:
                mod = KeyCondition.strToMod( mod, force_LR=True )
            else:
                raise TypeError
        except:
            print( ckit.strings["error_invalid_expression_for_argument"] % ("mod",), mod )
            return

        try:
            if vk in self.vk_mod_map:
                raise ValueError
        except:
            print( ckit.strings["error_already_defined_as_modifier"], vk_org )
            return

        self.vk_mod_map[vk] = mod

    ## 特定条件のウインドウのキーマップを定義する
    #
    #  @param self        -
    #  @param exe_name    ウインドウが所属するプログラムの実行ファイル名のディレクトリ名を取り除いた部分
    #  @param class_name  ウインドウのクラス名
    #  @param window_text ウインドウのタイトル文字列
    #  @param check_func  ウインドウ識別関数
    #  @return ウインドウごとのキーマップ
    #
    #  アプリケーションごと、あるいはウインドウごとに、それぞれ異なったキーのカスタマイズを行うために、
    #  実行ファイル名やウインドウの名前から、ウインドウの識別条件を定義します。\n\n
    #
    #  引数 exe_name, class_name, window_text に渡す文字列は、Keyhac のコンソールウインドウを使って、調査することが出来ます。
    #  タスクトレイ中の Keyhac のアイコンを右クリックして、[ 内部ログ ON ] を選択すると、コンソールウインドウに、
    #  フォーカス位置のウインドウの詳細情報が出力されるようになります。\n\n
    #
    #  引数 exe_name, class_name, window_text, check_func を省略するか None を渡した場合は、
    #  その条件を無視します。
    #
    #  引数 exe_name, class_name, window_text には、ワイルドカード ( * ? ) を使うことが出来ます。\n
    #
    #  check_func には、pyauto.Window オブジェクトを受け取り、True か False を返す関数を渡します。\n
    #  pyauto.Window クラスについては、pyauto のリファレンスを参照してください。\n
    #  http://hp.vector.co.jp/authors/VA012411/pyauto/doc/
    #
    def defineWindowKeymap( self, exe_name=None, class_name=None, window_text=None, check_func=None ):
        window_keymap = WindowKeymap( exe_name, class_name, window_text, check_func )
        self.window_keymap_list.append(window_keymap)
        return window_keymap

    ## マルチストローク用のキーマップを定義する
    def defineMultiStrokeKeymap( self, help_string=None ):
        keymap = WindowKeymap( help_string=help_string )
        return keymap

    def beginInput(self):
        self.input_seq = []
        self.virtual_modifier = self.modifier

    def endInput(self):
        self.setInput_Modifier(self.modifier)
        if self.debug : print( "OUT :", self.input_seq )
        pyauto.Input.send(self.input_seq)
        self.input_seq = []

    def setInput_Modifier( self, mod ):

        # Win と Alt の単体押しのキャンセルが必要かチェック
        # Win の単体押しは スタートメニューが開き、Alt の単体押しは メニューバーにフォーカスが移動してしまう。
        cancel_oneshot_win_alt = False
        if any((
            checkModifier( self.virtual_modifier, MODKEY_ALT ) and not hasModifier( mod, MODKEY_ALT),
            checkModifier( self.virtual_modifier, MODKEY_WIN ) and not hasModifier( mod, MODKEY_WIN ),
        )):
            cancel_oneshot_win_alt = True

        # Win と Alt の単体押しをキャンセル
        if cancel_oneshot_win_alt:
            self.input_seq.append( pyauto.Key( VK_LCONTROL ) )

        # モディファイア離す
        for vk_mod in self.vk_mod_map.items():
            if vk_mod[1] & MODKEY_USER_ALL : continue
            if ( vk_mod[1] & self.virtual_modifier ) and not ( vk_mod[1] & mod ):
                self.input_seq.append( pyauto.KeyUp(vk_mod[0]) )
                self.virtual_modifier &= ~vk_mod[1]

        # モディファイア押す
        for vk_mod in self.vk_mod_map.items():
            if vk_mod[1] & MODKEY_USER_ALL : continue
            if not ( vk_mod[1] & self.virtual_modifier ) and ( vk_mod[1] & mod ):
                self.input_seq.append( pyauto.KeyDown(vk_mod[0]) )
                self.virtual_modifier |= vk_mod[1]

        # Win と Alt の単体押しをキャンセル
        if cancel_oneshot_win_alt:
            self.input_seq.append( pyauto.Key( VK_LCONTROL ) )

    def setInput_FromString( self, s ):

        s = s.upper()

        vk = None
        mod = 0
        up = None

        token_list = s.split("-")

        for token in token_list[:-1]:

            token = token.strip()

            try:
                mod |= KeyCondition.strToMod( token, force_LR=True )
            except ValueError:
                if token=="D":
                    up = False
                elif token=="U":
                    up = True
                else:
                    raise ValueError

        token = token_list[-1].strip()

        vk = KeyCondition.strToVk(token)

        self.setInput_Modifier(mod)

        if vk in (VK_LBUTTON, VK_RBUTTON, VK_MBUTTON):

            x,y = pyauto.Input.getCursorPos()

            if vk==VK_LBUTTON:
                if up==True:
                    self.input_seq.append( pyauto.MouseLeftUp(x,y) )
                elif up==False:
                    self.input_seq.append( pyauto.MouseLeftDown(x,y) )
                else:
                    self.input_seq.append( pyauto.MouseLeftClick(x,y) )

            elif vk==VK_RBUTTON:
                if up==True:
                    self.input_seq.append( pyauto.MouseRightUp(x,y) )
                elif up==False:
                    self.input_seq.append( pyauto.MouseRightDown(x,y) )
                else:
                    self.input_seq.append( pyauto.MouseRightClick(x,y) )

            else: # VK_MBUTTON
                if up==True:
                    self.input_seq.append( pyauto.MouseMiddleUp(x,y) )
                elif up==False:
                    self.input_seq.append( pyauto.MouseMiddleDown(x,y) )
                else:
                    self.input_seq.append( pyauto.MouseMiddleClick(x,y) )
        else:
            if up==True:
                self.input_seq.append( pyauto.KeyUp(vk) )
            elif up==False:
                self.input_seq.append( pyauto.KeyDown(vk) )
            else:
                self.input_seq.append( pyauto.Key(vk) )

    # Win と Alt の単体押しをキャンセルする ( beginInput/endInput込み )
    # Win の単体押しは スタートメニューが開き、Alt の単体押しは メニューバーにフォーカスが移動してしまう。
    def _cancelOneshotWinAlt(self):
        if checkModifier( self.modifier, MODKEY_ALT ) or checkModifier( self.modifier, MODKEY_WIN ):
            self.beginInput()
            self.setInput_Modifier( self.modifier | MODKEY_CTRL_L )
            self.endInput()

    # フォーカスがあるウインドウを明示的に更新する
    def _updateFocusWindow(self):

        try:
            wnd = pyauto.Window.getFocus()
            if wnd==None:
                wnd = pyauto.Window.getForeground()
        except:
            wnd = None

        if wnd != self.wnd:
            self._focusChanged(wnd)


    # モディファイアのおかしな状態を修正する
    # たとえば Win-L を押して ロック画面に行ったときに Winキーが押されっぱなしになってしまうような現象を回避
    def _fixFunnyModifierState(self):

        for vk_mod in self.vk_mod_map.items():

            if vk_mod[1] & MODKEY_USER_ALL:
                continue

            if self.modifier & vk_mod[1]:
                state = pyauto.Input.getAsyncKeyState(vk_mod[0])
                if not (state & 0x8000):
                    self.modifier &= ~vk_mod[1]
                    if self.debug :
                        print( "" )
                        print( "FIX :", KeyCondition.vkToStr(vk_mod[0]) )
                        print( "" )


    # キーフックが強制解除されたことを検出し、フックを再設定する
    def checkSanity(self):

        if not self.hook_enabled : return

        state = [ pyauto.Input.getAsyncKeyState(vk_mod[0]) for vk_mod in self.vk_mod_map.items() ]
        if self.sanity_check_state != state:
            self.sanity_check_count += 1
            self.sanity_check_state = state
            if self.sanity_check_count >= 4:
                print( "" )
                print( ckit.strings["log_key_hook_force_cancellation_detected"] )
                print( "" )
                keyhac_hook.hook.reset()
                self.sanity_check_count = 0

    ## フックのなかで与えられた関数を実行する
    #
    #  @param self  -
    #  @param func  フックの中で実行する関数
    #
    #  Input.send() で実行する擬似的な入力の中に、物理的な入力を割り込ませないためには、
    #  Input.send() をフックのなかで実行する必要があります。
    #
    #  フックの外で command_InputKey などのキー入力機能を実行すると、
    #  稀に物理的なキー入力が擬似的なキー入力のなかに割り込んでしまい、
    #  意図しないキー操作になってしまったり、キーが押しっぱなしになってしまったり、
    #  といった問題が起きる可能性があります。
    #
    def hookCall( self, func ):
        self.hook_call_list.append(func)
        pyauto.Input.send( [ pyauto.KeyDown(0) ] )

    ## キーボードフォーカスを持っているウインドウを取得する
    #
    #  @return キーボードフォーカスを持っているpyauto.Windowオブジェクト
    #
    #  pyauto.Window クラスについては、pyauto のリファレンスを参照してください。\n
    #  http://hp.vector.co.jp/authors/VA012411/pyauto/doc/
    #
    def getWindow(self):
        return self.wnd

    ## キーボードフォーカスを持っているウインドウが所属するトップレベルウインドウを取得する
    #
    #  @return キーボードフォーカスを持っているウインドウが所属するトップレベル pyauto.Window オブジェクト
    #
    #  pyauto.Window クラスについては、pyauto のリファレンスを参照してください。\n
    #  http://hp.vector.co.jp/authors/VA012411/pyauto/doc/
    #
    def getTopLevelWindow(self):
        wnd = self.getWindow()
        if wnd==None : return None
        parent = wnd.getParent()
        while parent != pyauto.Window.getDesktop():
            wnd = parent;
            parent = wnd.getParent()
        return wnd


    ## バルーンヘルプを開く
    #
    #  @param   self    -
    #  @param   name    バルーンヘルプに付ける名前
    #  @param   text    ヘルプとして表示する文字列
    #  @param   timeout ヘルプを表示する時間(ミリ秒)
    #  @sa      closeBalloon
    #
    def popBalloon( self, name, text, timeout=None ):

        # キャレット位置またはフォーカスウインドウの左下位置を取得
        caret_wnd, caret_rect = pyauto.Window.getCaret()
        if caret_wnd:
            pos = caret_wnd.clientToScreen( caret_rect[0], caret_rect[3] )
        else:
            focus_wnd = pyauto.Window.getFocus()
            focus_client_rect = focus_wnd.getClientRect()
            pos = focus_wnd.clientToScreen( focus_client_rect[0], focus_client_rect[3] )

        # すでにバルーンがあったら閉じる
        self.closeBalloon()

        # バルーンウインドウの左上位置のDPIによってをフォントサイズ決定する
        dpi_scale = ckit.Window.getDisplayScalingFromPosition( pos[0], pos[1] )
        scaled_font_size = round( self.font_size * dpi_scale )
        font = ckit.getStockedFont( self.font_name, scaled_font_size )

        self.balloon = keyhac_balloon.BalloonWindow( self, font )
        self.balloon.setText( pos[0], pos[1], text )
        self.balloon_name = name

        if timeout:
            def onTimerCloseBalloon():
                self.closeBalloon(name)
            self.balloon_timer = onTimerCloseBalloon
            self.setTimer( self.balloon_timer, timeout )

    ## バルーンヘルプを閉じる
    #
    #  @param   self    -
    #  @param   name    バルーンヘルプを識別する文字列
    #  @sa      popBalloon
    #
    def closeBalloon( self, name=None ):

        if name==None or self.balloon_name==name:

            if self.balloon:
                self.balloon.destroy()

            self.balloon = None
            self.balloon_name = ""

            if self.balloon_timer:
                self.killTimer( self.balloon_timer )
                self.balloon_timer = None

    #--------------------------------------------------------
    # ここから下のメソッドはキーに割り当てることができる
    #--------------------------------------------------------


    ## キーを入力する関数を返す
    #
    #  @param self -
    #  @param keys 入力するキーのシーケンス (可変引数)
    #  @return キーを入力する関数
    #
    #  与えられたキーシーケンスを入力する関数を生成し、返します。
    #
    #  引数 keys には、 ( "A-Z", "A-X" ) のような、キー入力の文字列表現を渡します。
    #
    #  キーを入力する機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def InputKeyCommand( self, *keys ):

        def _inputKey():

            self.beginInput()

            for item in keys:

                if type(item)==str:
                    self.setInput_FromString(item)
                else:
                    raise TypeError;

            self.endInput()

        return _inputKey

    def command_InputKey( self, *keys ):
        print( ckit.strings["warning_api_deprecated"] % ("command_InputKey","InputKeyCommand") )
        return self.InputKeyCommand( *keys )


    ## 文字を入力する関数を返す
    #
    #  @param self -
    #  @param s    入力する文字
    #  @return 文字を入力する関数
    #
    #  与えられた文字列を入力する関数を生成し、返します。
    #
    #  文字列を入力する機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def InputTextCommand( self, s ):

        def _inputText():

            self.beginInput()

            self.setInput_Modifier(0)

            for c in s:
                self.input_seq.append( pyauto.Char(c) )

            self.endInput()

        return _inputText

    def command_InputText( self, s ):
        print( ckit.strings["warning_api_deprecated"] % ("command_InputText","InputTextCommand") )
        return self.InputTextCommand( s )


    ## キーボードマクロの記録を開始する
    #
    #  @param self -
    #
    def command_RecordStart(self):
        self.record_seq = []
        self.record_status = "recording"
        print( ckit.strings["log_macro_recording_started"] )
        self.popBalloon( "Record", ckit.strings["balloon_macro_recording_started"], 3000 )

    ## キーボードマクロの記録を終了する
    #
    #  @param self -
    #
    def command_RecordStop(self):

        if self.record_status=="recording":

            key_table = [ False ] * 256
            normalized_seq = []

            for vk, up in self.record_seq:
                if not up:
                    key_table[vk] = True
                    normalized_seq.append( [ vk, up, False ] ) # Upが来るまで未確定
                else:
                    if key_table[vk]:
                        key_table[vk] = False

                        for i in range(len(normalized_seq)-1,-1,-1):
                            if normalized_seq[i][0] == vk:
                                if normalized_seq[i][1]:
                                    break
                                else:
                                    normalized_seq[i][2] = True # Downを確定

                        normalized_seq.append( [ vk, up, True ] ) # 確定

            self.record_seq = []
            for vk, up, use in normalized_seq:
                if use:
                    self.record_seq.append( ( vk, up ) )

            self.record_status="recorded"

            print( ckit.strings["log_macro_recording_stopped"] )
            self.popBalloon( "Record", ckit.strings["balloon_macro_recording_stopped"], 3000 )

    ## キーボードマクロの記録を開始または終了する
    #
    #  @param self -
    #
    def command_RecordToggle(self):
        if self.record_status=="recording":
            return self.command_RecordStop()
        else:
            return self.command_RecordStart()

    ## キーボードマクロのを消去する
    #
    #  @param self -
    #
    def command_RecordClear(self):
        self.record_seq = None
        self.record_status = None
        print( ckit.strings["log_macro_recording_cleared"] )
        self.popBalloon( "Record", ckit.strings["balloon_macro_recording_cleared"], 3000 )

    ## キーボードマクロを再生する
    #
    #  @param self -
    #
    def command_RecordPlay(self):

        if self.record_status=="recorded":

            print( ckit.strings["log_macro_replay"] )

            # モディファイアを離す
            modifier = self.modifier
            input_seq = []
            for vk_mod in self.vk_mod_map.items():
                if self.modifier & vk_mod[1]:
                    input_seq.append( pyauto.KeyUp(vk_mod[0]) )
            pyauto.Input.send(input_seq)
            self.modifier = 0

            # 記録されたキーシーケンスを実行する
            for vk, up in self.record_seq:
                if not up:
                    if not self._onKeyDown(vk):
                        key_seq = [ pyauto.KeyDown(vk) ]
                        if self.debug : print( "OUT :", key_seq )
                        pyauto.Input.send(key_seq)
                else:
                    if not self._onKeyUp(vk):
                        key_seq = [ pyauto.KeyUp(vk) ]
                        if self.debug : print( "OUT :", key_seq )
                        pyauto.Input.send(key_seq)

            # モディファイアを戻す
            input_seq = []
            for vk_mod in self.vk_mod_map.items():
                if modifier & vk_mod[1]:
                    input_seq.append( pyauto.KeyDown(vk_mod[0]) )
            pyauto.Input.send(input_seq)
            self.modifier = modifier

    ## マウスカーソルを移動させる関数を返す
    #
    #  @param self    -
    #  @param delta_x 横方向の移動量(ピクセル単位)
    #  @param delta_y 縦方向の移動量(ピクセル単位)
    #  @return マウスカーソルを移動させる関数
    #
    #  与えられた移動量の、マウスカーソルを移動させる関数を生成し、返します。
    #
    #  マウスカーソルを移動させる機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def MouseMoveCommand( self, delta_x, delta_y ):

        def _mouseMove():

            x,y = pyauto.Input.getCursorPos()

            x += delta_x
            y += delta_y

            self.beginInput()

            self.input_seq.append( pyauto.MouseMove(x,y) )

            self.endInput()

        return _mouseMove

    def command_MouseMove( self, delta_x, delta_y ):
        print( ckit.strings["warning_api_deprecated"] % ("command_MouseMove","MouseMoveCommand") )
        return self.MouseMoveCommand( delta_x, delta_y )


    ## マウスのボタンを擬似的に押す関数を返す
    #
    #  @param self    -
    #  @param button ボタンを識別する文字列 ( 'left' / 'middle' / 'right' )
    #  @return マウスのボタンを擬似的に押す関数
    #
    #  マウスのボタンを擬似的に押す関数を生成し、返します。
    #
    #  マウスのボタンを擬似的に押す機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def MouseButtonDownCommand( self, button='left' ):

        def _mouseButtonDown():

            x,y = pyauto.Input.getCursorPos()

            self.beginInput()

            self.setInput_Modifier(0)

            mouse_input = None
            if button=='left':
                mouse_input = pyauto.MouseLeftDown(x,y)
            elif button=='middle':
                mouse_input = pyauto.MouseMiddleDown(x,y)
            elif button=='right':
                mouse_input = pyauto.MouseRightDown(x,y)
            else:
                print( ckit.strings["error_invalid_mouse_button_expression"], button )

            if mouse_input:
                self.input_seq.append( mouse_input )

            self.endInput()

        return _mouseButtonDown

    def command_MouseButtonDown( self, button='left' ):
        print( ckit.strings["warning_api_deprecated"] % ("command_MouseButtonDown","MouseButtonDownCommand") )
        return self.MouseButtonDownCommand( button )


    ## マウスのボタンを擬似的に離す関数を返す
    #
    #  @param self    -
    #  @param button ボタンを識別する文字列 ( 'left' / 'middle' / 'right' )
    #  @return マウスのボタンを擬似的に離す関数
    #
    #  マウスのボタンを擬似的に離す関数を生成し、返します。
    #
    #  マウスのボタンを擬似的に離す機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def MouseButtonUpCommand( self, button='left' ):

        def _mouseButtonUp():

            x,y = pyauto.Input.getCursorPos()

            self.beginInput()

            self.setInput_Modifier(0)

            mouse_input = None
            if button=='left':
                mouse_input = pyauto.MouseLeftUp(x,y)
            elif button=='middle':
                mouse_input = pyauto.MouseMiddleUp(x,y)
            elif button=='right':
                mouse_input = pyauto.MouseRightUp(x,y)
            else:
                print( ckit.strings["error_invalid_mouse_button_expression"], button )

            if mouse_input:
                self.input_seq.append( mouse_input )

            self.endInput()

        return _mouseButtonUp

    def command_MouseButtonUp( self, button='left' ):
        print( ckit.strings["warning_api_deprecated"] % ("command_MouseButtonUp","MouseButtonUpCommand") )
        return self.MouseButtonUpCommand( button )


    ## マウスのボタンを擬似的にクリックする関数を返す
    #
    #  @param self    -
    #  @param button ボタンを識別する文字列 ( 'left' / 'middle' / 'right' )
    #  @return マウスのボタンを擬似的にクリックする関数
    #
    #  マウスのボタンを擬似的にクリックする関数を生成し、返します。
    #
    #  マウスのボタンを擬似的にクリックする機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def MouseButtonClickCommand( self, button='left' ):

        def _mouseButtonClick():

            x,y = pyauto.Input.getCursorPos()

            self.beginInput()

            self.setInput_Modifier(0)

            mouse_input = None
            if button=='left':
                mouse_input = pyauto.MouseLeftClick(x,y)
            elif button=='middle':
                mouse_input = pyauto.MouseMiddleClick(x,y)
            elif button=='right':
                mouse_input = pyauto.MouseRightClick(x,y)
            else:
                print( ckit.strings["error_invalid_mouse_button_expression"], button )

            if mouse_input:
                self.input_seq.append( mouse_input )

            self.endInput()

        return _mouseButtonClick

    def command_MouseButtonClick( self, button='left' ):
        print( ckit.strings["warning_api_deprecated"] % ("command_MouseButtonClick","MouseButtonClickCommand") )
        return self.MouseButtonClickCommand( button )


    ## マウスのホイールを擬似的に回転する関数を返す
    #
    #  @param self    -
    #  @param wheel 回転量 (1.0=奥に向かって1クリック、-1.0=手前に向かって1クリック)
    #  @return マウスのホイールを擬似的に回転する関数
    #
    #  マウスのホイールを擬似的に回転する関数を生成し、返します。
    #
    #  マウスのホイールを擬似的に回転する機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def MouseWheelCommand( self, wheel ):

        def _mouseWheel():

            x,y = pyauto.Input.getCursorPos()

            self.beginInput()

            self.setInput_Modifier(0)

            self.input_seq.append( pyauto.MouseWheel(x,y,wheel) )

            self.endInput()

        return _mouseWheel

    def command_MouseWheel( self, wheel ):
        print( ckit.strings["warning_api_deprecated"] % ("command_MouseWheel","MouseWheelCommand") )
        return self.MouseWheelCommand( wheel )


    ## マウスの水平ホイールを擬似的に回転する関数を返す
    #
    #  @param self    -
    #  @param wheel 回転量 (1.0=奥に向かって1クリック、-1.0=手前に向かって1クリック)
    #  @return マウスの水平ホイールを擬似的に回転する関数
    #
    #  マウスの水平ホイールを擬似的に回転する関数を生成し、返します。
    #
    #  マウスの水平ホイールを擬似的に回転する機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def MouseHorizontalWheelCommand( self, wheel ):

        def _mouseHorizontalWheel():

            x,y = pyauto.Input.getCursorPos()

            self.beginInput()

            self.setInput_Modifier(0)

            self.input_seq.append( pyauto.MouseHorizontalWheel(x,y,wheel) )

            self.endInput()

        return _mouseHorizontalWheel

    def command_MouseHorizontalWheel( self, wheel ):
        print( ckit.strings["warning_api_deprecated"] % ("command_MouseHorizontalWheel","MouseHorizontalWheelCommand") )
        return self.MouseHorizontalWheelCommand( wheel )


    ## フォーカスされているウインドウを移動させる関数を返す
    #
    #  @param self    -
    #  @param delta_x 横方向の移動量(ピクセル単位)
    #  @param delta_y 縦方向の移動量(ピクセル単位)
    #  @return ウインドウを移動させる関数
    #
    #  与えられた移動量の、ウインドウを移動させる関数を生成し、返します。
    #
    #  ウインドウを移動させる機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def MoveWindowCommand( self, delta_x, delta_y ):

        def _moveWindow():
            wnd_top = self.getTopLevelWindow()
            rect = list(wnd_top.getRect())
            rect[0] += delta_x
            rect[1] += delta_y
            rect[2] += delta_x
            rect[3] += delta_y
            wnd_top.setRect(rect)

        return _moveWindow

    def command_MoveWindow( self, delta_x, delta_y ):
        print( ckit.strings["warning_api_deprecated"] % ("command_MoveWindow","MoveWindowCommand") )
        return self.MoveWindowCommand( delta_x, delta_y )


    ## フォーカスされているウインドウをモニターの端にそろえるように移動させる関数を返す
    #
    #  @param self      -
    #  @param direction 移動方向 (  0:左  1:上  2:右  3:下  )
    #  @return ウインドウを移動させる関数
    #
    #  与えられた方向にウインドウを移動させる関数を生成し、返します。
    #
    #  ウインドウを移動させる機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #
    def MoveWindowToMonitorEdgeCommand( self, direction ):

        def _intersectRect( rect1, rect2 ):
            intersect = list(rect1)
            intersect[0] = max( intersect[0], rect2[0] )
            intersect[1] = max( intersect[1], rect2[1] )
            intersect[2] = min( intersect[2], rect2[2] )
            intersect[3] = min( intersect[3], rect2[3] )
            return intersect

        def _moveWindowEdge():

            wnd_top = self.getTopLevelWindow()
            if not wnd_top: return

            wnd_rect = list(wnd_top.getRect())

            nearest = None
            farthest = None
            for monitor in pyauto.Window.getMonitorInfo():

                intersect_rect = _intersectRect( monitor[1], wnd_rect )
                intersect = False

                if direction==0 or direction==2:
                    if intersect_rect[1]<intersect_rect[3]:
                        intersect = True
                else:
                    if intersect_rect[0]<intersect_rect[2]:
                        intersect = True

                if intersect:
                    monitor_edge  = monitor[1][direction]
                    if direction<2:
                        if monitor_edge < wnd_rect[direction]:
                            if nearest==None or nearest<monitor_edge:
                                nearest=monitor_edge
                        if farthest==None or farthest>monitor_edge:
                            farthest=monitor_edge
                    else:
                        if monitor_edge > wnd_rect[direction]:
                            if nearest==None or nearest>monitor_edge:
                                nearest=monitor_edge
                        if farthest==None or farthest<monitor_edge:
                            farthest=monitor_edge

            if nearest==None:
                nearest=farthest

            if nearest!=None:
                delta = nearest-wnd_rect[direction]
                if direction==0 or direction==2:
                    wnd_rect[0] += delta
                    wnd_rect[2] += delta
                else:
                    wnd_rect[1] += delta
                    wnd_rect[3] += delta
                wnd_top.setRect(wnd_rect)

        return _moveWindowEdge

    def command_MoveWindow_MonitorEdge( self, direction ):
        print( ckit.strings["warning_api_deprecated"] % ("command_MoveWindow_MonitorEdge","MoveWindowToMonitorEdgeCommand") )
        return self.MoveWindowToMonitorEdgeCommand( direction )


    ## ウインドウをアクティブ化する関数を返す
    #
    #  @param self    -
    #  @param exe_name    ウインドウが所属するプログラムの実行ファイル名のディレクトリ名を取り除いた部分
    #  @param class_name  ウインドウのクラス名
    #  @param window_text ウインドウのタイトル文字列
    #  @param check_func  ウインドウ識別関数
    #  @param force       スレッドのインプット状態を切り替えるか否か
    #  @return ウインドウをアクティブ化する関数
    #
    #  与えられた条件のウインドウをアクティブ化する関数を生成し、返します。
    #
    #  引数 exe_name, class_name, window_text に渡す文字列は、Keyhac のコンソールウインドウを使って、調査することが出来ます。
    #  タスクトレイ中の Keyhac のアイコンを右クリックして、[ 内部ログ ON ] を選択すると、コンソールウインドウに、
    #  フォーカス位置のウインドウの詳細情報が出力されるようになります。
    #
    #  引数 exe_name, class_name, window_text, check_func を省略するか None を渡した場合は、
    #  その条件を無視します。
    #
    #  引数 exe_name, class_name, window_text には、ワイルドカード ( * ? ) を使うことが出来ます。
    #
    #  check_func には、pyauto.Window オブジェクトを受け取り、True か False を返す関数を渡します。
    #  pyauto.Window クラスについては、pyauto のリファレンスを参照してください。
    #  http://hp.vector.co.jp/authors/VA012411/pyauto/doc/
    #
    #  引数 force に True を与えると、スレッドのインプット状態を切り替えてから、ウインドウをフォアグラウンド化します。ウインドウをフォアグラウンドにしても、タスクバーのボタンが点滅する場合は、引数 force に True を与えてみてください。
    #
    #  ウインドウをアクティブ化する機能を持っているのは、この関数から返される関数であり、
    #  この関数自体はその機能を持っていないことに注意が必要です。
    #  また、ウインドウをアクティブ化する関数は、アクティブ化したWindow、または該当するWindowが見つからなかった場合はNoneを返します。
    #
    def ActivateWindowCommand( self, exe_name=None, class_name=None, window_text=None, check_func=None, force=False ):

        def _activateWindow():
            
            activated_wnd = [None]
            
            def callback( wnd, arg ):

                if not wnd.isVisible() : return True
                if wnd.isMinimized() : return True

                if exe_name     and not fnmatch.fnmatch( wnd.getProcessName(), exe_name ) : return True
                if class_name   and not fnmatch.fnmatch( wnd.getClassName(),   class_name ) : return True
                if window_text  and not fnmatch.fnmatch( wnd.getText(),        window_text ) : return True
                if check_func   and not check_func(wnd) : return True

                wnd = wnd.getLastActivePopup()
                wnd.setForeground(force)
                
                activated_wnd[0] = wnd
                
                return False

            pyauto.Window.enum( callback, None )
            
            return activated_wnd[0]

        return _activateWindow

    def command_ActivateWindow( self, exe_name=None, class_name=None, window_text=None, check_func=None, force=False ):
        print( ckit.strings["warning_api_deprecated"] % ("command_ActivateWindow","ActivateWindowCommand") )
        return self.ActivateWindowCommand( exe_name, class_name, window_text, check_func, force )


    ## プログラムを起動する関数を返す
    #
    #  @param self -
    #  @param verb          操作
    #  @param filename      操作対象のファイル
    #  @param param         操作のパラメータ
    #  @param directory     既定のディレクトリ
    #  @param swmode        表示状態
    #  @return プログラムを起動する関数
    #
    #  指定されたプログラムを起動する関数を生成し、返します。
    #
    #  引数verbには、実行する操作を文字列で渡します。指定可能な文字列は対象によって異なりますが、一般的には次のような操作が指定可能です。
    #
    #  open
    #       ファイルを開きます。またはプログラムを起動します。
    #  edit
    #       ファイルを編集します。
    #  properties
    #       ファイルのプロパティを表示します。
    #
    #  引数swmodeには、以下のいずれかの文字列(またはNone)を渡します。
    #
    #  "normal"または""またはNone
    #       アプリケーションを通常の状態で起動します。
    #  "maximized"
    #       アプリケーションを最大化状態で起動します。
    #  "minimized"
    #       アプリケーションを最小化状態で起動します。
    #
    #  詳細については、以下の解説を参照してください。\n
    #  http://msdn.microsoft.com/ja-jp/library/cc422072.aspx
    #
    #  プログラムの起動は、サブスレッドの中で行われます。
    #
    def ShellExecuteCommand( self, verb, filename, param, directory, swmode=None ):

        def _shellExecute():

            def jobShellExecute(job_item):
                pyauto.shellExecute( verb, filename, param, directory, swmode )

            def jobShellExecuteFinished(job_item):
                pass

            job_item = ckit.JobItem( jobShellExecute, jobShellExecuteFinished )
            ckit.JobQueue.defaultQueue().enqueue(job_item)

        return _shellExecute

    def command_ShellExecute( self, verb, filename, param, directory, swmode=None ):
        print( ckit.strings["warning_api_deprecated"] % ("command_ShellExecute","ShellExecuteCommand") )
        return self.ShellExecuteCommand( verb, filename, param, directory, swmode )


    ## リストウインドウを開き結果を取得する
    #
    #  @param   self     -
    #  @param   listers  リストのアイテムを列挙するオブジェクトのリスト
    #  @return 選択されたアイテム(キャンセル時 None) と モディファイアキー のタプル
    #
    def popListWindow( self, listers ):

        # １つしか開かない
        if self.list_window:
            return None, 0

        paste_target_wnd = pyauto.Window.getForeground()

        # キャレット位置またはフォーカスウインドウの左上位置を取得
        caret_wnd, caret_rect = pyauto.Window.getCaret()
        if caret_wnd:
            pos1 = caret_wnd.clientToScreen( caret_rect[0], caret_rect[1] )
            pos2 = caret_wnd.clientToScreen( caret_rect[2], caret_rect[3] )
        else:
            focus_wnd = pyauto.Window.getFocus()
            if not focus_wnd:
                print( ckit.strings["error_focus_not_found"] )
                return
            focus_client_rect = focus_wnd.getClientRect()
            pos1 = focus_wnd.clientToScreen( focus_client_rect[0], focus_client_rect[1] )
            pos2 = pos1
        caret_rect = ( pos1[0], pos1[1], pos2[0], pos2[1] )

        lister_select = 0

        def onStatusMessage( width, select ):
            return ""

        while True:

            # ちらつきを防止するために ListWindow の破棄を遅延する
            list_window_old = self.list_window

            title, lister = listers[lister_select]

            items = lister.getListItems()

            max_width = 80
            max_height = 16

            def onKeyDown( vk, mod ):

                if vk==VK_LEFT and mod==0:
                    if lister_select-1>=0:
                        self.list_window.switch_left = True
                        self.list_window.quit()
                    return True

                elif vk==VK_RIGHT and mod==0:
                    if lister_select+1<len(listers):
                        self.list_window.switch_right = True
                        self.list_window.quit()
                    return True

                elif vk==VK_DELETE and mod==0:
                    if hasattr(lister,"remove"):
                        select, mod = self.list_window.getResult()
                        lister.remove(select)
                        self.list_window.remove(select)
                    return True


            # リストウインドウの左上位置のDPIによってをフォントサイズ決定する
            dpi_scale = ckit.Window.getDisplayScalingFromPosition( pos1[0], pos1[1] )
            scaled_font_size = round( self.font_size * dpi_scale )
            font = ckit.getStockedFont( self.font_name, scaled_font_size )

            # 親ウインドウをフォアグラウンドにしないと、ListWindowがフォアグラウンドに来ない
            pyauto.Window.fromHWND( self.getHWND() ).setForeground(True)

            self.list_window = keyhac_listwindow.ListWindow( pos1[0], pos1[1], 5, 1, max_width, max_height, self, font, False, title, items, initial_select=0, return_modkey=True, keydown_hook=onKeyDown, onekey_search=False, statusbar_handler=onStatusMessage )
            self.list_window.lister = lister
            self.list_window.switch_left = False
            self.list_window.switch_right = False

            keyhac_misc.adjustWindowPosition( self.list_window, caret_rect )
            self.list_window.show(True,True)

            if list_window_old:
                list_window_old.destroy()

            self.list_window.messageLoop()

            if self.list_window.switch_left:
                if lister_select-1>=0:
                    lister_select -= 1
            elif self.list_window.switch_right:
                if lister_select+1<len(listers):
                    lister_select += 1
            else:
                break

        try:
            paste_target_wnd.setForeground()
        except:
            pass

        select, mod = self.list_window.getResult()
        self.list_window.destroy()
        self.list_window = None

        if select<0 :
            return None, 0

        return items[select], mod

    ## リストウインドウをキャンセルで閉じる
    def cancelListWindow(self):
        if self.list_window:
            self.list_window.cancel()

    ## リストウインドウが存在しているかを確認する
    def isListWindowOpened(self):
        return (self.list_window!=None)

    ## クリップボード履歴をリストウインドウで表示する
    def popClipboardList(self):

        item, mod = self.popListWindow( self.cblisters )
        if item==None : return

        if callable(item[1]):
            command = item[1]
            text = command()
        else:
            text = item[1]

        if not text: return

        # Ctrlを押しながら決定したときは、引用記号付で貼り付ける
        if mod & MODKEY_CTRL:
            lines = text.splitlines(True)
            text = ""
            for line in lines:
                text += self.quote_mark + line

        # Shiftを押しながら決定したときは、貼り付けを行わず、クリップボードに格納するだけ
        if mod & MODKEY_SHIFT:
            paste = False
        else:
            paste = True

        def jobPaste(job_item):

            time.sleep(0.05)

            wnd = None
            timeout = 0.5
            retry_time = 0.01
            while timeout>0.0:
                try:
                    wnd = pyauto.Window.getFocus()
                except:
                    time.sleep(retry_time)
                    timeout -= retry_time
                    continue
                if wnd==None:
                    time.sleep(retry_time)
                    timeout -= retry_time
                    continue
                break

            time.sleep(0.05)

            job_item.wnd = wnd

        def jobPasteFinished(job_item):
            ckit.setClipboardText(text)
            if paste:
                self.hookCall( self.InputKeyCommand("C-V") )

        job_item = ckit.JobItem( jobPaste, jobPasteFinished )
        ckit.JobQueue.defaultQueue().enqueue(job_item)


    ## クリップボード履歴をリスト表示する
    #
    #  @param self -
    #
    #  クリップボード履歴をリスト表示します。
    #
    #  クリップボード履歴を選択し、Enterキーを押すことで、ペーストすることが出来ます。
    #  Fキーを押して、インクリメンタルサーチをすることが出来ます。
    #
    def command_ClipboardList(self):

        # すでに開いていたら閉じる
        if self.isListWindowOpened():
            self.cancelListWindow()
            return

        # キーボードフックの中で長時間処理できないので、DelayedCallをつかってリストを表示する
        self.delayedCall( self.popClipboardList, 0 )


    ## クリップボード履歴の直近のアイテムを削除する
    #
    #  @param self -
    #
    #  クリップボード履歴の直近のアイテムを削除して、一つ前のアイテムをアクティブにします。
    #
    def command_ClipboardRemove(self):
        self.cancelListWindow()
        self.clipboard_history.pop()


    ## クリップボード履歴の直近のアイテムを末尾に回す
    #
    #  @param self -
    #
    #  クリップボード履歴の直近のアイテムを末尾に回して、一つ前のアイテムをアクティブにします。
    #
    def command_ClipboardRotate(self):
        self.cancelListWindow()
        self.clipboard_history.rotate()

    ## config.py を再読み込みする
    def command_ReloadConfig(self):
        self.configure()
        print( ckit.strings["log_config_reloaded"] )
        print( "" )

    ## config.py を編集する
    def command_EditConfig(self):

        def jobEditConfig(job_item):
            self.editConfigFile()

        def jobEditConfigFinished(job_item):
            print( ckit.strings["log_config_editor_launched"] )
            print( "" )

        job_item = ckit.JobItem( jobEditConfig, jobEditConfigFinished )
        ckit.JobQueue.defaultQueue().enqueue(job_item)

## @} keymap

