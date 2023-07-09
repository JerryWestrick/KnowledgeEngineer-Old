# Knowledge Engineer Tool
# GUI interface based on Svelte

Here I used the Svelte javascript framework to create a simple GUI for KET.

This file contains some tips and explanations on how the development process works.  In order for this GUI to work it needs to be served via the Twisted Web Server, as it requires WebSocket connection to it.

1. **SETUP**: Svelte development includes pre-compiling source code to "executable".  The source code is in the "src" directory.  The executable is in the "public" directory.  Twisted should publish the "public" directory.  The setup was created with the following the description [here](https://cabreraalex.medium.com/svelte-js-flask-combining-svelte-with-a-simple-backend-server-d1bc46190ab9)  .

2. **Compiling**: I usually compile by running npm run dev in the www-svelte directory.  This will compile and present a web server offer access to the web page.  This web page does not connect correctly to the twisted web server.  But it does compile the code which twistd servers.  It is possible to start an autobuild process without the web service as noted in the document above; but I have not tried it.



More to come