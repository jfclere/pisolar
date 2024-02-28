Don't use arduino-ide_2.1.1 it is broken for attiny45

Use arduino-1.8.19 (tested 2023/09/24)
```
[jfclere@pc-100 arduino-1.8.19]$ ./arduino
Picked up JAVA_TOOL_OPTIONS: 
Gtk-Message: 09:22:04.734: Failed to load module "pk-gtk-module"
Sketch uses 2200 bytes (53%) of program storage space. Maximum is 4096 bytes.
Global variables use 91 bytes (35%) of dynamic memory, leaving 165 bytes for local variables. Maximum is 256 bytes.
```

Note the value: 600 and 800 (should be 725 for the 12V version).
