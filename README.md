# indigo-prowl
Using this plugin, you don't need to have Growl installed on your system: it utilizes the Prowl API directly.

Prowl is a simple app that allows you to send arbitrary notifications to your iOS devices.  By installing it for Indigo, you'll be
able to send push notifications as actions.  It does require a one-time purchase to get the app. After installing the app on your device,
notifications are first processed by Prowl and then able to redirect to Indigo (note that I haven't implemented this feature yet).  You
can also try out sending push notifications from the Prowl website to get a sense for how the system works.

You will need to have a Prowl API key for your application.  These are free to generate on the Prowl site.  I would recommend creating
a specific key for this application.  After installing the plugin, you will be prompted to enter a valid API key to enable Prowl support
in Indigo.

After installing, you will be able to select "Prowl Notify" from the notifications menu in your actions.  I'm still experimenting with this,
so it's unclear how far I'll take it...  For now, please enjoy and let me know if you have any questions or issues!
