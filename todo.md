DONE

1. DONE: Integrate keyboard [ OK ] with the screen which called the kb
1. (Pre-req to keyrepeat, and bug fix for the above) Reimplement long press so it only occurs on keyup. I'll need to define the min-max keydown time. Try 200-700ms, so keyrepeat is over 700ms.
1. Implement keyrepeat
    is_long_pressed is not working

NEXT:

1. Add flashing cursor to keyboard
    1. consider adding a new repeating, low-priority interrupt... simpler than keeping track of even more tick_ms values!
1. What _is_ actually next? What is my aim with this? Park it and move on?
1. Consider having the old style non-key-repeat button action when in menus. It would select an item on-time-elapsed-with-key-down instead of on-keyup-when-press-duration-is-long-ish.
    1. I had started down this route with start_keyrepeat() which was supposed to control the keyrepeat when in keyboard mode and long_press when in menu ui mode.
1. Consider extending the UI to use a 4 way joystick... although WebUI is probably more useful
1. Investigate: WebUSB in MicroPython. This would probably be a different project, as there would be less need for an OLED based UI. Can a web server be run over USB? That would be ideal for initial config (instead of the onscreen keyboard)





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
