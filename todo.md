DONE
1. DONE: Integrate keyboard [ OK ] with the screen which called the kb

NEXT:
bug: one long press event can run into another. e.g. [ Ok ] on keyboard navigates back to main screen, keep holding key, and it goes back into keyboard. Each new long press event needs a keyup event to reset it. This will link to keyrepeat which will require a change to long press so that it only activates on keyup

1. (Pre-req to keyrepeat, and bug fix for the above) Reimplement long press so it only occurs on keyup. I'll need to define the min-max keydown time. Try 200-700ms, so keyrepeat is over 700ms.
2. Implement keyrepeat
3. Add flashing cursor to keyboard





ONCE Refamiliar with Code:

split UI so that the Menu is separate from the Screen, and possibly Navigation is something else
All menus could be stored in one object

shown as json, but implemented with python objects
*/

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