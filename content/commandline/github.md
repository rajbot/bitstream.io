Title:  Adding a `git hub` alias
Author: raj
Tags:   git, github

This git alias will open a web browser and take you to a project's github page when you
type `git hub` in a checked-out project directory.

For OS X:

    :::bash
    git config --global alias.hub '!open $(echo $(git config --get remote.origin.url) | perl -pe "s|git\@github\.com:|https://github.com/|")'

For Linux:

    :::bash
    git config --global alias.hub '!xdg-open $(echo $(git config --get remote.origin.url) |perl -pe "s|git\@github\.com:|https://github.com/|")'
