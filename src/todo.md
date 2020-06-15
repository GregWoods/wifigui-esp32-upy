/*
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