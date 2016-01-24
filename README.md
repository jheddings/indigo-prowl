# indigo-prowl

Prowl is a simple app that allows you to send arbitrary notifications to your iOS devices.  By installing it for Indigo, you'll be
able to send push notifications as actions.  Because this plugin adds native Prowl support to Indigo, you do not have to have Growl
installed on your system.

## Requirements

[Indigo Pro](https://www.indigodomo.com) is required to get support for plugins.  If you haven't tried Indigo and are interested in home
automation, please give it a shot right away...  You won't be disappointed!

To use this plugin, you will need a free [Prowl](http://www.prowlapp.com/) account.  If you already have an account, you are already
one step ahead of the game!

After creating your Prowl account, you will need to [create an API key](https://www.prowlapp.com/api_settings.php).  Even if you have
an existing API key, create a new one specifically for this application.  Be sure to keep this API key handy, you'll need it later.

You will also need the Prowl app installed in your mobile device.  There are no subscription fees, just the one-time cost for the app.
After purchasing, open the app and be sure to allow notifications (that's why we are doing this after all).  You can also send a message
using their [online tool](https://www.prowlapp.com/add_notification.php) to try it out.

## Installation

This plugin is installed like any other Indigo plugin.  Visit the [releases](https://github.com/jheddings/indigo-prowl/releases) page
and download the latest version.  For advanced users, you may also clone the source tree directly into your Indigo plugins folder, making
updates as easy as pull & reload.

Once downloaded, extract the zip file and double-click the Prowl.indigoPlugin package.  Note that you must do this on the same computer
that is running your Indigo server.  If there is already a version of the plugin installed, Indigo will prompt you to replace it with the
newer version.

## Configuration

After installing the first time, you will be prompted for the plugin configuration.  You can also access the plugin config at any time
from the Plugins menu.

The 'Application Name' is useful for identifying the source of the push messages.  It is visible on each notification.  By default, the
application will show up as 'Indigo' for all messages.

The 'API Key' is the same key you [created earlier](https://www.prowlapp.com/api_settings.php) (you did that, right?).

Occasionally, it is useful to see the debugging information to troubleshoot problems.  Feel free to enable debugging, but it will get
rather noisy if left on all the time.

## Usage

After you have installed and configured the plugin, you can start to send messages as actions.  For the type of action, select
'Notification Actions' and 'Prowl Notify'.  Then press 'Edit Action Settings' and you will be prompted for the following information.

Your message may include a 'Title', which will be displayed on the notification.  This could be an event type, such as Weather, or any
value you'd like.  It is not required.

The message must include a body, specified in the 'Message' property.

Your message may also provide a 'Priority', which determines how the message is handled by Prowl.

Both the 'Title' and 'Message' allow standard variable and state substitutions.  Simply insert `%%v:VARIABLEID%%` anywhere in the text
as many times as you want. `VARIABLEID` is the variable's numeric id as found in the UI. Likewise, you can substitute device state values
by inserting `%%d:DEVICEID:STATEKEY%%` where `DEVICEID` is the device's numeric id and the STATEKEY is the state identifier as found in the
doucumentation for built-in devices and in the Custom States tile in the control area of the Home screen for custom plugin devices.

## Updates

From the plugin's menu, select "Check for Updates" to look for newer releases of the plugin.  Any updates will be displayed in the
Indigo event log.
