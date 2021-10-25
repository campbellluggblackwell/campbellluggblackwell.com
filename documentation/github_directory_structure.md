# An introduction to this GitHub structure

The group site is here:

https://github.com/campbellluggblackwell

Within that site, there is a Repository:

https://github.com/campbellluggblackwell/campbellluggblackwell.com

.  Because you are reading this file, you are likely in that repository.  Be sure not to confuse this repository with
   the actual campbellluggblackwell.com site.  You add and make changes to files here.  They are then published to the
   actual site.

The repository has the following directories:

  - .github/workflows
  - documentation
  - old_rootsweb_website
  - scripts
  - website

These are explained (out of order) below:

### https://github.com/campbellluggblackwell/campbellluggblackwell.com/tree/main/website
This directory contains all the files for the website.  If you change files or add/remove files in this directory, that change
is automatically applied to the actual BlueHost website.  Most changes happen here.  Don't worry too much about making a mistake.  GitHub remembers each change.  There are many versions of each of the files.  If there is a problem, we can always go back to an older version.

### https://github.com/campbellluggblackwell/campbellluggblackwell.com/tree/main/scripts
This directory contains Python scripts that can do various tasks "in bulk".  For instance, we wanted to add metadata to all \*.html files.  Instead of doing that manually for each file, we wrote a script to do it.  Contained in this directory are several such scripts.  If you ever need to do something on some or all of the files, its helpful to write a script.  This certainly isn't a requirement.  Some changes are a combination of running a script and manual edits and that's OK too!

### https://github.com/campbellluggblackwell/campbellluggblackwell.com/tree/main/old_rootsweb_website
Before being hosted on BlueHost, the website was part of "Rootsweb".  When we migrated to the new site, we made a copy of the old one just in case something went wrong.  You won't see many changes here.  In time, we may even delete this directory once we are sure all content has been moved to the new website in `/website`

### https://github.com/campbellluggblackwell/campbellluggblackwell.com/tree/main/documentation
This directory hopefully containing lots of helpful information describing the work which is performed.

### https://github.com/campbellluggblackwell/campbellluggblackwell.com/tree/main/.github/workflows
This directory contains the scripts which publish the files from `/website` to the actual website on BlueHost.  Github can be automated.  For every checkin, you can have it do something.  For instance, you could setup a script in this directory to email you every time someone made a change.  Or, maybe run a check every time someone checks something in.  We use it to publish the website.  This is a little more tricky than most of the other things here, but it really isn't bad and you can likely pick it up once you get oriented with what its doing.  A write-up of this directory and the process is given here: https://github.com/campbellluggblackwell/campbellluggblackwell.com/blob/main/documentation/how_the_site_is_published.md

