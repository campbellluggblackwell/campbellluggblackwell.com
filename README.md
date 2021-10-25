# campbellluggblackwell.com
Repository for cambellluggblackwell.com website

Contents for the website should go in "/website/".  The 'main' branch is what actually gets sent to http://campbellluggblackwell.com which is hosted on BlueHost.

To make changes, you can change /main/ directly.  However, if you want someone to review them first, or they aren't quite ready, create
a new branch and put your changes there.  Later a pull request can be made to get it integrated into 'main' for you.  This is the safe
way to make changes because anything you do can always be repaired (actually anything can be repaired, so don't worry about making a
mistake).

Github can be configured to automatically run scripts when things change.  We do two things:
- We update a "sample" website.  This is at: https://github.com/campbellluggblackwell/campbellluggblackwell.github.io  This 
  sample site is only somewhat useful.  It might be used to determine if a problem was with something in Github or something
  on our web server.  Generally this isn't used for much
- We update the real site on Bluehost.  This is the cool part.  To update our website, you simply change files here on GitHub
  They are then automatically copied to our website on BlueHost.  This process is detailed in other files here.
  
