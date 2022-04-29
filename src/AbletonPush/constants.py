from enum import Enum

"""
0x47 - Manufacturers ID
0x7F - System Exclusive Device ID
0x15 - Product model ID
"""
SYSEX_PREFIX_PUSH = [71, 127, 21]


class MIDIType(Enum):
    ControlChange = 0
    Note = 1
    Pitch = 3
    Touch = 4


class LightTypes(Enum):
    White = 0
    Red = 1
    Green = 2
    Yellow = 3
    Blue = 4
    RedYellow = 5
    RGB = 6
    NoLight = 7


class LightColorRedYellow(Enum):
    Black = 0
    RedDim = 1
    RedDimBlinkSlow = 2
    RedDimBlinkFast = 3
    RedLit = 4
    RedLitBlinkSlow = 5
    RedLitBlinkFast = 6
    YellowDim = 7
    YellowDimBlinkSlow = 8
    YellowDimBlinkFast = 9
    YellowLit = 10
    YellowLitBlinkSlow = 11
    YellowLitBlinkFast = 12
    LimeDim = 13
    LimeDimBlinkSlow = 14
    LimeDimBlinkFast = 15
    LimeLit = 16
    LimeLitBlinkSlow = 17
    LimeLitBlinkFast = 18
    GreenDim = 19
    GreenDimBlinkSlow = 20
    GreenDimBlinkFast = 21
    GreenLit = 22
    GreenLitBlinkSlow = 23
    GreenLitBlinkFast = 24


class LightColorSingle(Enum):
    Black = 0
    Dim = 1
    DimBlinkSlow = 2
    DimBlinkFast = 3
    Lit = 4
    LitBlinkSlow = 5
    LitBlinkFast = 6


class TouchStripModes(Enum):
    FollowTouchReturnToMiddleLock = 0
    BarAdjustTouchBottomLock = 1
    BarAdjustTouchMiddleLock = 2
    FollowTouchStaticLock = 3
    Addressable = 4
    FollowTouchReturnToMiddle = 5
    BarAdjustTouchBottom = 6
    BarAdjustTouchMiddle = 7
    FollowTouchStatic = 8
    MiddleStatic = 15


class PushTextCharacters(Enum):
    ArrowSlimUp = '↑'
    ArrowSlimDown = '↓'
    BarThreeHorizontal = '≡'
    VerticalWithMidDottedRight = '꜏'
    VerticalWithMidDottedLeft = '꜊'
    LineDoubleVertical = '‖'
    DashDoubleHorizontal = '╌'
    Folder = '📁'
    DashDoubleVertical = '╎'
    DegreeSign = '°'
    LetterAWithDiaeresisCapital = 'Ä'
    LetterCWithCedillaCapital = 'Ç'
    LetterOWithDiaeresisCapital = 'Ö'
    LetterUWithDiaeresisCapital = 'Ü'
    SharpSCapital = 'ẞ'
    LetterAWithGraveSmall = 'à'
    LetterAWithDiaeresisSmall = 'ä'
    LetterCWithCedillaSmall = 'ç'
    LetterEWithGraveSmall = 'è'
    LetterEWithAcuteSmall = 'é'
    LetterEWithCircumflexSmall = 'ê'
    LetterIWithCircumflexSmall = 'î'
    LetterNWithTildeSmall = 'ñ'
    LetterOWithDiaeresisSmall = 'ö'
    DivisionSign = '÷'
    LetterOWithStrokeSmall = 'ø'
    LetterUWithDiaeresisSmall = 'ü'
    MusicFlat = '♭'
    EllipsisHorizontal = '…'
    BlockFull = '█'
    ArrowSlimRight = '→'
    ArrowSlimLeft = '←'
    Space = ' '
    ExclamationMark = '!'
    QuotationMark = '"'
    NumberSign = '#'
    DollarSign = '$'
    PercentSign = '%'
    Ampersand = '&'
    Apostrophe = "'"
    ParenthesisLeft = '('
    ParenthesisRight = ')'
    Asterisk = '*'
    PlusSign = '+'
    Comma = ','
    HyphenMinus = '-'
    FullStop = '.'
    SlashSolidus = '/'
    DigitZero = '0'
    DigitOne = '1'
    DigitTwo = '2'
    DigitThree = '3'
    DigitFour = '4'
    DigitFive = '5'
    DigitSix = '6'
    DigitSeven = '7'
    DigitEight = '8'
    DigitNine = '9'
    Colon = ':'
    SemiColon = ';'
    LessThanSign = '<'
    EqualsSign = '='
    GreaterThanSign = '>'
    QuestionMark = '?'
    AtSignCommercialAt = '@'
    LetterACapital = 'A'
    LetterBCapital = 'B'
    LetterCCapital = 'C'
    LetterDCapital = 'D'
    LetterECapital = 'E'
    LetterFCapital = 'F'
    LetterGCapital = 'G'
    LetterHCapital = 'H'
    LetterICapital = 'I'
    LetterJCapital = 'J'
    LetterKCapital = 'K'
    LetterLCapital = 'L'
    LetterMCapital = 'M'
    LetterNCapital = 'N'
    LetterOCapital = 'O'
    LetterPCapital = 'P'
    LetterQCapital = 'Q'
    LetterRCapital = 'R'
    LetterSCapital = 'S'
    LetterTCapital = 'T'
    LetterUCapital = 'U'
    LetterVCapital = 'V'
    LetterWCapital = 'W'
    LetterXCapital = 'X'
    LetterYCapital = 'Y'
    LetterZCapital = 'Z'
    SquareBracketLeft = '['
    SolidusReverse = '\\'
    SquareBracketRight = ']'
    CircumflexAccent = '^'
    UnderscoreLowLine = '_'
    GraveAccent = '`'
    LetterASmall = 'a'
    LetterBSmall = 'b'
    LetterCSmall = 'c'
    LetterDSmall = 'd'
    LetterESmall = 'e'
    LetterFSmall = 'f'
    LetterGSmall = 'g'
    LetterHSmall = 'h'
    LetterISmall = 'i'
    LetterJSmall = 'j'
    LetterKSmall = 'k'
    LetterLSmall = 'l'
    LetterMSmall = 'm'
    LetterNSmall = 'n'
    LetterOSmall = 'o'
    LetterPSmall = 'p'
    LetterQSmall = 'q'
    LetterRSmall = 'r'
    LetterSSmall = 's'
    LetterTSmall = 't'
    LetterUSmall = 'u'
    LetterVSmall = 'v'
    LetterWSmall = 'w'
    LetterXSmall = 'x'
    LetterYSmall = 'y'
    LetterZSmall = 'z'
    CurlyBracketLeft = '{'
    VerticalLine = '|'
    CurlyBracketRight = '}'
    Tilde = '~'
    TrianglePointingRight = '▶'


PUSH_TEXT_CAHRACTER_SET_DICT = {
    PushTextCharacters.ArrowSlimUp.value: 0,
    PushTextCharacters.ArrowSlimDown.value: 1,
    PushTextCharacters.BarThreeHorizontal.value: 2,
    PushTextCharacters.VerticalWithMidDottedRight.value: 3,
    PushTextCharacters.VerticalWithMidDottedLeft.value: 4,
    PushTextCharacters.LineDoubleVertical.value: 5,
    PushTextCharacters.DashDoubleHorizontal.value: 6,
    PushTextCharacters.Folder.value: 7,
    PushTextCharacters.DashDoubleVertical.value: 8,
    PushTextCharacters.DegreeSign.value: 9,
    PushTextCharacters.LetterAWithDiaeresisCapital.value: 10,
    PushTextCharacters.LetterCWithCedillaCapital.value: 11,
    PushTextCharacters.LetterOWithDiaeresisCapital.value: 12,
    PushTextCharacters.LetterUWithDiaeresisCapital.value: 13,
    PushTextCharacters.SharpSCapital.value: 14,
    PushTextCharacters.LetterAWithGraveSmall.value: 15,
    PushTextCharacters.LetterAWithDiaeresisSmall.value: 16,
    PushTextCharacters.LetterCWithCedillaSmall.value: 17,
    PushTextCharacters.LetterEWithGraveSmall.value: 18,
    PushTextCharacters.LetterEWithAcuteSmall.value: 19,
    PushTextCharacters.LetterEWithCircumflexSmall.value: 20,
    PushTextCharacters.LetterIWithCircumflexSmall.value: 21,
    PushTextCharacters.LetterNWithTildeSmall.value: 22,
    PushTextCharacters.LetterOWithDiaeresisSmall.value: 23,
    PushTextCharacters.DivisionSign.value: 24,
    PushTextCharacters.LetterOWithStrokeSmall.value: 25,
    PushTextCharacters.LetterUWithDiaeresisSmall.value: 26,
    PushTextCharacters.MusicFlat.value: 27,
    PushTextCharacters.EllipsisHorizontal.value: 28,
    PushTextCharacters.BlockFull.value: 29,
    PushTextCharacters.ArrowSlimRight.value: 30,
    PushTextCharacters.ArrowSlimLeft.value: 31,
    PushTextCharacters.Space.value: 32,
    PushTextCharacters.ExclamationMark.value: 33,
    PushTextCharacters.QuotationMark.value: 34,
    PushTextCharacters.NumberSign.value: 35,
    PushTextCharacters.DollarSign.value: 36,
    PushTextCharacters.PercentSign.value: 37,
    PushTextCharacters.Ampersand.value: 38,
    PushTextCharacters.Apostrophe.value: 39,
    PushTextCharacters.ParenthesisLeft.value: 40,
    PushTextCharacters.ParenthesisRight.value: 41,
    PushTextCharacters.Asterisk.value: 42,
    PushTextCharacters.PlusSign.value: 43,
    PushTextCharacters.Comma.value: 44,
    PushTextCharacters.HyphenMinus.value: 45,
    PushTextCharacters.FullStop.value: 46,
    PushTextCharacters.SlashSolidus.value: 47,
    PushTextCharacters.DigitZero.value: 48,
    PushTextCharacters.DigitOne.value: 49,
    PushTextCharacters.DigitTwo.value: 50,
    PushTextCharacters.DigitThree.value: 51,
    PushTextCharacters.DigitFour.value: 52,
    PushTextCharacters.DigitFive.value: 53,
    PushTextCharacters.DigitSix.value: 54,
    PushTextCharacters.DigitSeven.value: 55,
    PushTextCharacters.DigitEight.value: 56,
    PushTextCharacters.DigitNine.value: 57,
    PushTextCharacters.Colon.value: 58,
    PushTextCharacters.SemiColon.value: 59,
    PushTextCharacters.LessThanSign.value: 60,
    PushTextCharacters.EqualsSign.value: 61,
    PushTextCharacters.GreaterThanSign.value: 62,
    PushTextCharacters.QuestionMark.value: 63,
    PushTextCharacters.AtSignCommercialAt.value: 64,
    PushTextCharacters.LetterACapital.value: 65,
    PushTextCharacters.LetterBCapital.value: 66,
    PushTextCharacters.LetterCCapital.value: 67,
    PushTextCharacters.LetterDCapital.value: 68,
    PushTextCharacters.LetterECapital.value: 69,
    PushTextCharacters.LetterFCapital.value: 70,
    PushTextCharacters.LetterGCapital.value: 71,
    PushTextCharacters.LetterHCapital.value: 72,
    PushTextCharacters.LetterICapital.value: 73,
    PushTextCharacters.LetterJCapital.value: 74,
    PushTextCharacters.LetterKCapital.value: 75,
    PushTextCharacters.LetterLCapital.value: 76,
    PushTextCharacters.LetterMCapital.value: 77,
    PushTextCharacters.LetterNCapital.value: 78,
    PushTextCharacters.LetterOCapital.value: 79,
    PushTextCharacters.LetterPCapital.value: 80,
    PushTextCharacters.LetterQCapital.value: 81,
    PushTextCharacters.LetterRCapital.value: 82,
    PushTextCharacters.LetterSCapital.value: 83,
    PushTextCharacters.LetterTCapital.value: 84,
    PushTextCharacters.LetterUCapital.value: 85,
    PushTextCharacters.LetterVCapital.value: 86,
    PushTextCharacters.LetterWCapital.value: 87,
    PushTextCharacters.LetterXCapital.value: 88,
    PushTextCharacters.LetterYCapital.value: 89,
    PushTextCharacters.LetterZCapital.value: 90,
    PushTextCharacters.SquareBracketLeft.value: 91,
    PushTextCharacters.SolidusReverse.value: 92,
    PushTextCharacters.SquareBracketRight.value: 93,
    PushTextCharacters.CircumflexAccent.value: 94,
    PushTextCharacters.UnderscoreLowLine.value: 95,
    PushTextCharacters.GraveAccent.value: 96,
    PushTextCharacters.LetterASmall.value: 97,
    PushTextCharacters.LetterBSmall.value: 98,
    PushTextCharacters.LetterCSmall.value: 99,
    PushTextCharacters.LetterDSmall.value: 100,
    PushTextCharacters.LetterESmall.value: 101,
    PushTextCharacters.LetterFSmall.value: 102,
    PushTextCharacters.LetterGSmall.value: 103,
    PushTextCharacters.LetterHSmall.value: 104,
    PushTextCharacters.LetterISmall.value: 105,
    PushTextCharacters.LetterJSmall.value: 106,
    PushTextCharacters.LetterKSmall.value: 107,
    PushTextCharacters.LetterLSmall.value: 108,
    PushTextCharacters.LetterMSmall.value: 109,
    PushTextCharacters.LetterNSmall.value: 110,
    PushTextCharacters.LetterOSmall.value: 111,
    PushTextCharacters.LetterPSmall.value: 112,
    PushTextCharacters.LetterQSmall.value: 113,
    PushTextCharacters.LetterRSmall.value: 114,
    PushTextCharacters.LetterSSmall.value: 115,
    PushTextCharacters.LetterTSmall.value: 116,
    PushTextCharacters.LetterUSmall.value: 117,
    PushTextCharacters.LetterVSmall.value: 118,
    PushTextCharacters.LetterWSmall.value: 119,
    PushTextCharacters.LetterXSmall.value: 120,
    PushTextCharacters.LetterYSmall.value: 121,
    PushTextCharacters.LetterZSmall.value: 122,
    PushTextCharacters.CurlyBracketLeft.value: 123,
    PushTextCharacters.VerticalLine.value: 124,
    PushTextCharacters.CurlyBracketRight.value: 125,
    PushTextCharacters.Tilde.value: 126,
    PushTextCharacters.TrianglePointingRight.value: 127,
}

PUSH_TEXT_CAHRACTER_SET_ALTERNATIVES_DICT = {
    'å': PUSH_TEXT_CAHRACTER_SET_DICT[PushTextCharacters.LetterASmall.value],
    'Å': PUSH_TEXT_CAHRACTER_SET_DICT[PushTextCharacters.LetterACapital.value],
}


ButtonGridColorsRGB = {
    0: (0x00, 0x00, 0x00),  # BlackBlack
    1: (0x1E, 0x1E, 0x1E),  # GreyEerieBlack
    2: (0x7F, 0x7F, 0x7F),  # GreyGray
    3: (0xFF, 0xFF, 0xFF),  # WhiteWhite
    4: (0xFF, 0x4C, 0x4C),  # RedTartOrange
    5: (0xFF, 0x00, 0x00),  # RedRed
    6: (0x59, 0x00, 0x00),  # RedBloodRed
    7: (0x19, 0x00, 0x00),  # BrownDiesel
    8: (0xFF, 0xBD, 0x6C),  # YellowMellowApricot
    9: (0xFF, 0x54, 0x00),  # OrangeMysticRed
    10: (0x59, 0x1D, 0x00),  # BrownSealBrown
    11: (0x27, 0x1B, 0x00),  # BrownZinnwalditeBrown
    12: (0xFF, 0xFF, 0x4C),  # YellowLemonYellow
    13: (0xFF, 0xFF, 0x00),  # YellowYellow
    14: (0x59, 0x59, 0x00),  # GreenDarkBronzeCoin
    15: (0x19, 0x19, 0x00),  # BrownBlackChocolate
    16: (0x88, 0xFF, 0x4C),  # GreenKiwi
    17: (0x54, 0xFF, 0x00),  # GreenChlorophyllGreen
    18: (0x1D, 0x59, 0x00),  # GreenJapaneseLaurel
    19: (0x14, 0x2B, 0x00),  # GreenBlackChocolate
    20: (0x4C, 0xFF, 0x4C),  # GreenScreamingGreen
    21: (0x00, 0xFF, 0x00),  # GreenLime
    22: (0x00, 0x59, 0x00),  # GreenDarkGreenX11
    23: (0x00, 0x19, 0x00),  # GreenVampireBlack
    24: (0x4C, 0xFF, 0x5E),  # GreenScreamingGreen2
    25: (0x00, 0xFF, 0x19),  # GreenElectricGreen
    26: (0x00, 0x59, 0x0D),  # GreenEmeraldGreen
    27: (0x00, 0x19, 0x02),  # GreenVampireBlack2
    28: (0x4C, 0xFF, 0x88),  # GreenVeryLightMalachiteGreen
    29: (0x00, 0xFF, 0x55),  # GreenMalachite
    30: (0x00, 0x59, 0x1D),  # GreenForestGreenTraditional
    31: (0x00, 0x1F, 0x12),  # GreenBurnham
    32: (0x4C, 0xFF, 0xB7),  # BlueAquamarineBright
    33: (0x00, 0xFF, 0x99),  # GreenMediumSpringGreen
    34: (0x00, 0x59, 0x35),  # GreenCastletonGreen
    35: (0x00, 0x19, 0x12),  # GreenSwamp
    36: (0x4C, 0xC3, 0xFF),  # BluePictonBlue
    37: (0x00, 0xA9, 0xFF),  # BlueDeepSkyBlue
    38: (0x00, 0x41, 0x52),  # GreenMidnightGreenEagleGreen
    39: (0x00, 0x10, 0x19),  # GreenRichBlackFOGRA29
    40: (0x4C, 0x88, 0xFF),  # BlueDodgerBlue
    41: (0x00, 0x55, 0xFF),  # BlueNavyBlue
    42: (0x00, 0x1D, 0x59),  # BlueOxfordBlue
    43: (0x00, 0x08, 0x19),  # BlueBlueCharcoal
    44: (0x4C, 0x4C, 0xFF),  # BlueUltramarineBlue
    45: (0x00, 0x00, 0xFF),  # BlueBlue
    46: (0x00, 0x00, 0x59),  # BlueStratos
    47: (0x00, 0x00, 0x19),  # BlueBlackRussian
    48: (0x87, 0x4C, 0xFF),  # BlueLavenderIndigo
    49: (0x54, 0x00, 0xFF),  # VioletElectricUltramarine
    50: (0x19, 0x00, 0x64),  # BlueDeepViolet
    51: (0x0F, 0x00, 0x30),  # VioletBlackRussian
    52: (0xFF, 0x4C, 0xFF),  # RedShockingPinkCrayola
    53: (0xFF, 0x00, 0xFF),  # VioletMagentaFuchsia
    54: (0x59, 0x00, 0x59),  # VioletImperialPurple
    55: (0x19, 0x00, 0x19),  # VioletSmokyBlack
    56: (0xFF, 0x4C, 0x87),  # RedSasquatchSocks
    57: (0xFF, 0x00, 0x54),  # RedTorchRed
    58: (0x59, 0x00, 0x1D),  # RedDarkScarlet
    59: (0x22, 0x00, 0x13),  # VioletLicorice
    60: (0xFF, 0x15, 0x00),  # RedCandyAppleRed
    61: (0x99, 0x35, 0x00),  # BrownBrown
    62: (0x79, 0x51, 0x00),  # BrownDarkBronze
    63: (0x43, 0x64, 0x00),  # GreenMetallicGreen
    64: (0x03, 0x39, 0x00),  # GreenDarkGreen
    65: (0x00, 0x57, 0x35),  # GreenAquaDeep
    66: (0x00, 0x54, 0x7F),  # BlueDarkCerulean
    67: (0x00, 0x00, 0xFF),  # BlueBlueDuplicate
    68: (0x00, 0x45, 0x4F),  # GreenSherpaBlue
    69: (0x25, 0x00, 0xCC),  # BlueInterdimensionalBlue
    70: (0x7F, 0x7F, 0x7F),  # GreyGray2
    71: (0x20, 0x20, 0x20),  # GreyRaisinBlack
    72: (0xFF, 0x00, 0x00),  # RedRed2
    73: (0xBD, 0xFF, 0x2D),  # GreenGreenYellow
    74: (0xAF, 0xED, 0x06),  # GreenSpringBud
    75: (0x64, 0xFF, 0x09),  # GreenBrightGreen
    76: (0x10, 0x8B, 0x00),  # GreenIndiaGreen
    77: (0x00, 0xFF, 0x87),  # GreenGuppieGreen
    78: (0x00, 0xA9, 0xFF),  # BlueDeepSkyBlueDuplicate
    79: (0x00, 0x2A, 0xFF),  # BlueBlueBright
    80: (0x3F, 0x00, 0xFF),  # BlueElectricUltramarine
    81: (0x7A, 0x00, 0xFF),  # VioletViolet
    82: (0xB2, 0x1A, 0x7D),  # VioletMediumVioletRed
    83: (0x40, 0x21, 0x00),  # BrownCola
    84: (0xFF, 0x4A, 0x00),  # OrangeInternationalOrangeAerospace
    85: (0x88, 0xE1, 0x06),  # GreenAlienArmpit
    86: (0x72, 0xFF, 0x15),  # GreenLawnGreen
    87: (0x00, 0xFF, 0x00),  # GreenLimeDuplicate
    88: (0x3B, 0xFF, 0x26),  # GreenNeonGreen
    89: (0x59, 0xFF, 0x71),  # GreenSeaGreen2
    90: (0x38, 0xFF, 0xCC),  # BlueBrightTurquoise
    91: (0x5B, 0x8A, 0xFF),  # BlueBlueberry
    92: (0x31, 0x51, 0xC6),  # BlueCeruleanBlue
    93: (0x87, 0x7F, 0xE9),  # BlueMediumPurple
    94: (0xD3, 0x1D, 0xFF),  # VioletVividOrchid
    95: (0xFF, 0x00, 0x5D),  # RedFolly
    96: (0xFF, 0x7F, 0x00),  # OrangeOrange
    97: (0xB9, 0xB0, 0x00),  # YellowGreenCitrus
    98: (0x90, 0xFF, 0x00),  # GreenMangoGreen
    99: (0x83, 0x5D, 0x07),  # BrownYukonGold
    100: (0x39, 0x2B, 0x00),  # BrownAmericanBronze
    101: (0x14, 0x4C, 0x10),  # GreenParsley
    102: (0x0D, 0x50, 0x38),  # GreenBlueGreen
    103: (0x15, 0x15, 0x2A),  # BlueMidnightExpress
    104: (0x16, 0x20, 0x5A),  # BlueMidnightBlue
    105: (0x69, 0x3C, 0x1C),  # BrownPullmanBrownUPSBrown
    106: (0xA8, 0x00, 0x0A),  # RedDarkCandyAppleRed
    107: (0xDE, 0x51, 0x3D),  # RedCarminePink
    108: (0xD8, 0x6A, 0x1C),  # BrownChocolate
    109: (0xFF, 0xE1, 0x26),  # YellowBananaYellow
    110: (0x9E, 0xE1, 0x2F),  # GreenOliveDrab3
    111: (0x67, 0xB5, 0x0F),  # GreenKellyGreen
    112: (0x1E, 0x1E, 0x30),  # BlueDarkGunmetal
    113: (0xDC, 0xFF, 0x6B),  # GreenBoogerBuster
    114: (0x80, 0xFF, 0xBD),  # BlueAquamarine
    115: (0x9A, 0x99, 0xFF),  # BlueMaximumBluePurple
    116: (0x8E, 0x66, 0xFF),  # BlueVioletsAreBlue
    117: (0x40, 0x40, 0x40),  # GreyBlackOlive
    118: (0x75, 0x75, 0x75),  # GreySonicSilver
    119: (0xE0, 0xFF, 0xFF),  # BlueLightCyan
    120: (0xA0, 0x00, 0x00),  # RedBrightRed
    121: (0x35, 0x00, 0x00),  # BrownBlackBean
    122: (0x1A, 0xD0, 0x00),  # GreenYellowGreen
    123: (0x07, 0x42, 0x00),  # GreenDeepFir
    124: (0xB9, 0xB0, 0x00),  # YellowGreenCitrusDuplicate
    125: (0x3F, 0x31, 0x00),  # BrownDarkBronzeCoin
    126: (0xB3, 0x5F, 0x00),  # OrangeWindsorTan
    127: (0x4B, 0x15, 0x02),  # BrownFrenchPuce
}


class ButtonGridColors(Enum):
    BlackBlack = 0
    GreyEerieBlack = 1
    GreyGray = 2
    WhiteWhite = 3
    RedTartOrange = 4
    RedRed = 5
    RedBloodRed = 6
    BrownDiesel = 7
    YellowMellowApricot = 8
    OrangeMysticRed = 9
    BrownSealBrown = 10
    BrownZinnwalditeBrown = 11
    YellowLemonYellow = 12
    YellowYellow = 13
    GreenDarkBronzeCoin = 14
    BrownBlackChocolate = 15
    GreenKiwi = 16
    GreenChlorophyllGreen = 17
    GreenJapaneseLaurel = 18
    GreenBlackChocolate = 19
    GreenScreamingGreen = 20
    GreenLime = 21
    GreenDarkGreenX11 = 22
    GreenVampireBlack = 23
    GreenScreamingGreen2 = 24
    GreenElectricGreen = 25
    GreenEmeraldGreen = 26
    GreenVampireBlack2 = 27
    GreenVeryLightMalachiteGreen = 28
    GreenMalachite = 29
    GreenForestGreenTraditional = 30
    GreenBurnham = 31
    BlueAquamarineBright = 32
    GreenMediumSpringGreen = 33
    GreenCastletonGreen = 34
    GreenSwamp = 35
    BluePictonBlue = 36
    BlueDeepSkyBlue = 37
    GreenMidnightGreenEagleGreen = 38
    GreenRichBlackFOGRA29 = 39
    BlueDodgerBlue = 40
    BlueNavyBlue = 41
    BlueOxfordBlue = 42
    BlueBlueCharcoal = 43
    BlueUltramarineBlue = 44
    BlueBlue = 45
    BlueStratos = 46
    BlueBlackRussian = 47
    BlueLavenderIndigo = 48
    VioletElectricUltramarine = 49
    BlueDeepViolet = 50
    VioletBlackRussian = 51
    RedShockingPinkCrayola = 52
    VioletMagentaFuchsia = 53
    VioletImperialPurple = 54
    VioletSmokyBlack = 55
    RedSasquatchSocks = 56
    RedTorchRed = 57
    RedDarkScarlet = 58
    VioletLicorice = 59
    RedCandyAppleRed = 60
    BrownBrown = 61
    BrownDarkBronze = 62
    GreenMetallicGreen = 63
    GreenDarkGreen = 64
    GreenAquaDeep = 65
    BlueDarkCerulean = 66
    BlueBlueDuplicate = 67
    GreenSherpaBlue = 68
    BlueInterdimensionalBlue = 69
    GreyGray2 = 70
    GreyRaisinBlack = 71
    RedRed2 = 72
    GreenGreenYellow = 73
    GreenSpringBud = 74
    GreenBrightGreen = 75
    GreenIndiaGreen = 76
    GreenGuppieGreen = 77
    BlueDeepSkyBlueDuplicate = 78
    BlueBlueBright = 79
    BlueElectricUltramarine = 80
    VioletViolet = 81
    VioletMediumVioletRed = 82
    BrownCola = 83
    OrangeInternationalOrangeAerospace = 84
    GreenAlienArmpit = 85
    GreenLawnGreen = 86
    GreenLimeDuplicate = 87
    GreenNeonGreen = 88
    GreenSeaGreen2 = 89
    BlueBrightTurquoise = 90
    BlueBlueberry = 91
    BlueCeruleanBlue = 92
    BlueMediumPurple = 93
    VioletVividOrchid = 94
    RedFolly = 95
    OrangeOrange = 96
    YellowGreenCitrus = 97
    GreenMangoGreen = 98
    BrownYukonGold = 99
    BrownAmericanBronze = 100
    GreenParsley = 101
    GreenBlueGreen = 102
    BlueMidnightExpress = 103
    BlueMidnightBlue = 104
    BrownPullmanBrownUPSBrown = 105
    RedDarkCandyAppleRed = 106
    RedCarminePink = 107
    BrownChocolate = 108
    YellowBananaYellow = 109
    GreenOliveDrab3 = 110
    GreenKellyGreen = 111
    BlueDarkGunmetal = 112
    GreenBoogerBuster = 113
    BlueAquamarine = 114
    BlueMaximumBluePurple = 115
    BlueVioletsAreBlue = 116
    GreyBlackOlive = 117
    GreySonicSilver = 118
    BlueLightCyan = 119
    RedBrightRed = 120
    BrownBlackBean = 121
    GreenYellowGreen = 122
    GreenDeepFir = 123
    YellowGreenCitrusDuplicate = 124
    BrownDarkBronzeCoin = 125
    OrangeWindsorTan = 126
    BrownFrenchPuce = 127


class ButtonGridColorsBrightness(Enum):
    White0 = ButtonGridColors.BlackBlack.value
    White12 = ButtonGridColors.GreyEerieBlack.value
    White50 = ButtonGridColors.GreyGray.value
    White100 = ButtonGridColors.WhiteWhite.value
    Red65 = ButtonGridColors.RedTartOrange.value
    Red50 = ButtonGridColors.RedRed.value
    Red17 = ButtonGridColors.RedBloodRed.value
    Red05 = ButtonGridColors.BrownDiesel.value
    OrangeMysticRed71 = ButtonGridColors.YellowMellowApricot.value
    OrangeMysticRed50 = ButtonGridColors.OrangeMysticRed.value
    OrangeMysticRed17 = ButtonGridColors.BrownSealBrown.value
    OrangeMysticRed08 = ButtonGridColors.BrownZinnwalditeBrown.value
    Yellow65 = ButtonGridColors.YellowLemonYellow.value
    Yellow50 = ButtonGridColors.YellowYellow.value
    Yellow17 = ButtonGridColors.GreenDarkBronzeCoin.value
    Yellow05 = ButtonGridColors.BrownBlackChocolate.value
    GreenBright65 = ButtonGridColors.GreenKiwi.value
    GreenBright50 = ButtonGridColors.GreenChlorophyllGreen.value
    GreenBright17 = ButtonGridColors.GreenJapaneseLaurel.value
    GreenBright08 = ButtonGridColors.GreenBlackChocolate.value
    GreenLime65 = ButtonGridColors.GreenScreamingGreen.value
    GreenLime50 = ButtonGridColors.GreenLime.value
    GreenLime17 = ButtonGridColors.GreenDarkGreenX11.value
    GreenLime05 = ButtonGridColors.GreenVampireBlack.value
    GreenElectric65 = ButtonGridColors.GreenScreamingGreen2.value
    GreenElectric50 = ButtonGridColors.GreenElectricGreen.value
    GreenElectric17 = ButtonGridColors.GreenEmeraldGreen.value
    GreenElectric05 = ButtonGridColors.GreenVampireBlack2.value
    GreenMalachite65 = ButtonGridColors.GreenVeryLightMalachiteGreen.value
    GreenMalachite50 = ButtonGridColors.GreenMalachite.value
    GreenMalachite17 = ButtonGridColors.GreenForestGreenTraditional.value
    GreenMalachite06 = ButtonGridColors.GreenBurnham.value
    Cyan65 = ButtonGridColors.BlueAquamarineBright.value
    Cyan50 = ButtonGridColors.GreenMediumSpringGreen.value
    Cyan17 = ButtonGridColors.GreenCastletonGreen.value
    Cyan05 = ButtonGridColors.GreenSwamp.value
    BlueDeepSky65 = ButtonGridColors.BluePictonBlue.value
    BlueDeepSky50 = ButtonGridColors.BlueDeepSkyBlue.value
    BlueDeepSky16 = ButtonGridColors.GreenMidnightGreenEagleGreen.value
    BlueDeepSky05 = ButtonGridColors.GreenRichBlackFOGRA29.value
    BlueNavy65 = ButtonGridColors.BlueDodgerBlue.value
    BlueNavy50 = ButtonGridColors.BlueNavyBlue.value
    BlueNavy17 = ButtonGridColors.BlueOxfordBlue.value
    BlueNavy05 = ButtonGridColors.BlueBlueCharcoal.value
    Blue65 = ButtonGridColors.BlueUltramarineBlue.value
    Blue50 = ButtonGridColors.BlueBlue.value
    Blue17 = ButtonGridColors.BlueStratos.value
    Blue05 = ButtonGridColors.BlueBlackRussian.value
    VioletElectricUltramarine65 = ButtonGridColors.BlueLavenderIndigo.value
    VioletElectricUltramarine50 = ButtonGridColors.VioletElectricUltramarine.value
    VioletElectricUltramarine20 = ButtonGridColors.BlueDeepViolet.value
    VioletElectricUltramarine09 = ButtonGridColors.VioletBlackRussian.value
    VioletMagenta65 = ButtonGridColors.RedShockingPinkCrayola.value
    VioletMagenta50 = ButtonGridColors.VioletMagentaFuchsia.value
    VioletMagenta17 = ButtonGridColors.VioletImperialPurple.value
    VioletMagenta05 = ButtonGridColors.VioletSmokyBlack.value
    RedTorch65 = ButtonGridColors.RedSasquatchSocks.value
    RedTorch50 = ButtonGridColors.RedTorchRed.value
    RedTorch17 = ButtonGridColors.RedDarkScarlet.value
    RedTorch07 = ButtonGridColors.VioletLicorice.value
