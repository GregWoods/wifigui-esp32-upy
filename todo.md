DONE

1. DONE: Integrate keyboard [ OK ] with the screen which called the kb
1. (Pre-req to keyrepeat, and bug fix for the above) Reimplement long press so it only occurs on keyup. I'll need to define the min-max keydown time. Try 200-700ms, so keyrepeat is over 700ms.

NEXT:

1. Implement keyrepeat
1. Add flashing cursor to keyboard
1. Investigate: WebUSB in MicroPython. Can a web server be run over USB? That would be ideal for initial config (instead of the onscreen keyboard)





All menus could be stored in one object
shown as json, but implemented with python objects


```json
"Navigation" : {
    "CurrentItem" : { "CurrentMenuIdx" : 0, "CurrentItemIdx" : 0 }, //setter will navigate to new Menu
    "Menus": [
        "Menu" : {
            "MenuItems": [
                "MenuItem" : {
                    "Type" : "",
                    "Text" : "",
                    "NavigateTo": { "MenuIdx" : 1, "ItemIdx" : 1"},
                    "OnPress" : ""      //a function
                }
            ]
        }
    ]



```