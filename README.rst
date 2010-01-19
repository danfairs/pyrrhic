Pyrrhic
=======

Pyrrhic is a simple interactive command-line HTTP client, designed to help 
test RESTful web APIs.

Pyrrhic is alpha software. It's not feature complete, but it's complete 
enough to be of some use. Here's the to do list:

  * Saving and loading of resource sets
  * Colourised output of responses
  * HTTP HEAD support
  * Ability to define, save and load named data payloads
  * Cookie management
  * Ability to set arbitrary request headers
  * Ability to preview the request before it's sent
  * Consider whether it's worth using mechanize or zope.testbrowser as 
    the underlying engine
  * Probably lots more

Installation
------------

Pyrrhic can be installed with ``pip`` or ``easy_install`` in the usual way::

  pip install pyrrhic
  easy_install pyrrhic
  
This will download and instally pyrrhic and its dependencies, and create
a ``pyr`` script in your Python's bin directory.

Usage
-----

To start Pyrrhic, type ``pyr`` at the command prompt::

  $ pyr
  pyr >>>
  

Getting Help
~~~~~~~~~~~~

Type ``h`` at the pyr prompt to get a list of commands.

Press Ctrl-D to exit.

Resources
~~~~~~~~~

The key concept in Pyrrhic is a resource. A resource is essentially a named URL.
Pyrrhic will show you all the defined resources with the 's' command. By default,
there are none defined::

  pyr >>> s
  pyr >>>
  
Let's add one::

  pyr >>> r http://news.bbc.co.uk/
  pyr >>> s
  __default__		http://news.bbc.co.uk:80
  pyr >>>
  
When you add a resource like that, it becomes the default resource. Adding another
resource replaces it::

  pyr >>> r http://www.bbc.co.uk/
  pyr >>> s
  __default__		http://www.bbc.co.uk:80
  pyr >>>
  
Pyrrhic can remember other URLs though, if you name them::

  pyr >>> r news.bbc.co.uk news
  pyr >>> s
  __default__		http://www.bbc.co.uk:80
  news		http://news.bbc.co.uk:80
  
Note that Pyrrhic will assume http as the URL scheme.

Of course, now we have a couple of resources defined, we want to interact with them.
Pyrrhic supports the HTTP methods ``GET``, ``POST``, ``PUT``, ``DELETE`` and ``OPTIONS``.
To invoke a ``GET`` on the default resource, simply do::

  pyr >>> get
  pyr >>> get
  200 OK
  content-length: 111272
  accept-ranges: bytes
  expires: Tue, 19 Jan 2010 14:55:42 GMT
  server: Apache
  connection: close
  pragma: no-cache
  cache-control: max-age=0
  date: Tue, 19 Jan 2010 14:55:42 GMT
  content-type: text/html
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-GB" lang="en-GB">
  <head profile="http://dublincore.org/documents/dcq-html/">

  <title>BBC - Homepage</title>
    ... etc ...
    
As you can see, Pyrrhic will show the HTTP status code and message, all
headers, and the response body.

You can also similarly work with a named resource::

  pyr >>> get news
  pyr >>> get news
  200 OK
  transfer-encoding: chunked
  accept-ranges: bytes
  expires: Tue, 19 Jan 2010 14:58:04 GMT
  vary: Host
  keep-alive: timeout=10, max=678
  server: Apache
  connection: close
  cache-control: max-age=0
  date: Tue, 19 Jan 2010 14:58:04 GMT
  content-type: text/html
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xml:lang="en-GB" xmlns="http://www.w3.org/1999/xhtml" lang="en-GB">
  <head> 
  <title>BBC NEWS | News Front Page</title>
  
The HTTP verbs ``OPTIONS`` and ``DELETE`` work in a similar way::

  pyr >>> del
  405 Method Not Allowed
  ... etc ...
  pyr >>> opts news
  pyr >>> opts news
  200 OK
  content-length: 0
  expires: Tue, 19 Jan 2010 15:00:21 GMT
  vary: Host
  keep-alive: timeout=10, max=733
  server: Apache
  connection: close
  allow: GET,HEAD,POST,OPTIONS,TRACE
  cache-control: max-age=0
  date: Tue, 19 Jan 2010 15:00:21 GMT
  content-type: text/html
  pyr >>>
  
In both cases, omitting the resource name works on the default resource.

Supplying Data
~~~~~~~~~~~~~~

``POST`` and ``PUT`` methods can have data supplied to them. You should supply
this in a querystring-like format. As with GET, you can specify a named resource
or work with the default resource::

   pyr >>> post :key1=value1&key2=value2
   200 OK
   ... etc ...
   pyr >>> post :key1=value1 news
   200 OK
   ... etc ...
   pyr >>> put :key1=value1
   405 Method Not Allowed
   

Basic Authorisation
~~~~~~~~~~~~~~~~~~~

You can attach basic authorisation credentials to a resource::

  pyr >>> auth username password
  pyr >>> auth username password news
  
As before, omitting the resource name applies the change to the default resource.
All subsequent requests with that resource will use the authorisation headers.
  
Contributing to Pyrrhic
-----------------------

If you want to extend Pyrrhic, please go ahead! The code is on github:

  http://github.com/danfairs/pyrrhic
  
Fork the repository and make your changes, then send me a pull request for review.
It would be great if you could write tests for any of your changes. 

Tests
-----

To run the Pyrrhic test suite, you'll need ``mock`` and ``nose``. You may 
need to install these by hand using ``pip`` or ``easy_install`` as before. 
In fact, I'd recommend the following::

  94:$ sudo apt-get install python-virtualenv
  94:~ dan$ virtualenv pyrrhic
  New python executable in pyrrhic/bin/python
  Installing setuptools............done.
  94:~ dan$ cd pyrrhic/
  94:pyrrhic dan$ source bin/activate
  (pyrrhic)94:pyrrhic dan$ git clone git://github.com/danfairs/pyrrhic.git
  Initialized empty Git repository in /Users/dan/pyrrhic/pyrrhic/.git/
  remote: Counting objects: 210, done.
  remote: Compressing objects: 100% (163/163), done.
  remote: Total 210 (delta 91), reused 110 (delta 42)
  Receiving objects: 100% (210/210), 28.10 KiB | 5 KiB/s, done.
  Resolving deltas: 100% (91/91), done.
  (pyrrhic)94:pyrrhic dan$ cd pyrrhic/
  (pyrrhic)94:pyrrhic dan$ python setup.py develop
  running develop
  running egg_info
  ... etc ...
  Installing pyr script to /Users/dan/pyrrhic/bin
  Installed /Users/dan/pyrrhic/pyrrhic
  Processing dependencies for pyrrhic==0.0dev
  Finished processing dependencies for pyrrhic==0.0dev
  (pyrrhic)94:pyrrhic dan$ pip install mock nose
  Downloading/unpacking nose
  Downloading/unpacking mock
  Successfully installed mock nose
  (pyrrhic)94:pyrrhic dan$ cd pyrrhic
  (pyrrhic)94:pyrrhic dan$ nosetests
  ..................................................................
  ----------------------------------------------------------------------
  Ran 66 tests in 0.023s

  OK





