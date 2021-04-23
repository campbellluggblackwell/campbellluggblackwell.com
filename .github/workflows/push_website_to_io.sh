# Shell script to run during the push_website_to_io.yml action
# This runs in the virtual environment created when the action is triggered

# Log in
git config --global user.email robert.lugg@gmail.com
git config --global user.name robertlugg

# When the action is executed the first operation is to clone the repository and run this script.
# The directory ./source will already exist before running this script
git clone --single-branch --branch $GITHUB_REF https://${{ secrets.API_TOKEN_GITHUB }}@github.com/campbellluggblackwell/campbellluggblackwell.com.git source

# Get the github.io repository so this script can modify it
git clone --single-branch --branch main https://${{ secrets.API_TOKEN_GITHUB }}@github.com/campbellluggblackwell/campbellluggblackwell.github.io.git destination
- run: ls
- run: |
       rm -Rf destination/$GITHUB_REF
       mkdir destination/$GITHUB_REF
       cp -R source/website/* destination/$GITHUB_REF
- run: ls destination
- run: |
       cd destination
       rm -Rf index.html
       echo "Previews for campbellluggblackwell.com" > index.html
       echo "Go to child directories to see all branches. For instance, go to this site /main to see the website on the main branch" >> index.html
       echo "<a href="main">main branch</a>" >> index.html
       git add --all
       # git diff-index : to avoid doing the git commit failing if there are no changes to be commit
       git diff-index --quiet HEAD || git commit --message "Don't edit this file.  Integration on `date` from website directory"
       git push origin --set-upstream main
