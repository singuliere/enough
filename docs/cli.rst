Introduction
============

The enough CLI controls the infrastructure.

Installation
============

* Install Docker http://docs.docker.com/engine/installation/

* Copy the following to ``~/.bashrc``::

    eval "$(docker run --rm enoughcommunity/enough:latest install)"

* Verify that it works::

    enough --help

Release management
==================

* Prepare a new version

 - version=1.3.0 ; perl -pi -e "s/^version.*/version = $version/" setup.cfg ; for i in 1 2 ; do python setup.py sdist ; amend=$(git log -1 --oneline | grep --quiet "version $version" && echo --amend) ; git commit $amend -m "version $version" ChangeLog setup.cfg ; git tag -a -f -m "version $version" $version ; done

* Publish a new version

 - python setup.py sdist
 - twine upload --username singuliere --password "$PYPI_PASSWORD" dist/enough-$version.tar.gz
 - git push ; git push --tags
 - docker rmi enoughcommunity/enough
 - python -m enough.internal.cmd build image
 - docker tag enough:$version enoughcommunity/enough:$version
 - docker tag enough:$version enoughcommunity/enough:latest
 - docker login
 - docker push enoughcommunity/enough:latest
 - docker push enoughcommunity/enough:$version

* pypi maintenance

 - python setup.py register # if the project does not yet exist
 - trim old versions at https://pypi.python.org/pypi/enough
