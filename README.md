# udemy-dl
**A cross-platform python based utility to download courses from udemy for personal offline use.**

[![download.png](https://s24.postimg.org/v4ajcjn9x/download.png)](https://postimg.org/image/egj1a1si9/)

### Requirements

- Python 2.7.x
- Python module requests
- Python module colorama

### Install modules

	pip install -r requirements.txt

	
### Tested on

- Windows 7/8
- Kali linux (2017.1)
- Mac OSX 10.9

	 
### Download udemy-dl

You can download the latest version of udemy-dl by cloning the GitHub repository.

	git clone https://github.com/r0oth3x49/udemy-dl.git


### Advanced Usage

<pre><code>
Author: Nasir khan (<a href="http://r0oth3x49.herokuapp.com/">r0ot h3x49</a>)

Usage: udemy-dl.py [-h] [-u "username"] [-p "password"] COURSE_URL
                   [-s] [-l] [-r VIDEO_QUALITY] [-o OUTPUT] 

Options:
  General:
    -h, --help        Shows the help.
    -v, --version     Shows the version.

  Advance:
    -u, --username    Username in udemy.
    -p, --password    Password of your account.
    -s, --save-links  Do not download but save links to a file.
    -l, --list-infos  Just list all lectures and their name with resolution.
    -r, --resolution  Download video resolution, default resolution is 720p.
    -o, --output      Output directory where the videos will be saved, default
                      is current directory.
  
  Example:
	python udemy-dl.py -u user@domain.com -p P45sw0rd https://www.udemy.com/course_name/
</code></pre>
