# udemy-dl
**A cross-platform python based utility to download courses from udemy for personal offline use.**

[![download.png](https://s24.postimg.org/v4ajcjn9x/download.png)](https://postimg.org/image/egj1a1si9/)

### Requirements

- Python (2 or 3)
- Python `pip`
- Python module `requests`
- Python module `colorama`

### Install modules

	pip install -r requirements.txt
	
### Tested on

- Windows 7/8
- Kali linux (2017.1)
- Mac OSX 10.9

	 
### Download udemy-dl

You can download the latest version of udemy-dl by cloning the GitHub repository.

	git clone https://github.com/r0oth3x49/udemy-dl.git


### Usage 

***Downloading course***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd https://www.udemy.com/COURSE_NAME
	
***Downloading Course with specific resolution***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd https://www.udemy.com/COURSE_NAME -r 720
	
***Downloading course to a specific location***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd https://www.udemy.com/COURSE_NAME -o "/path/to/directory/"
	
***Downloading course with specific resolution to a specific location***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd https://www.udemy.com/COURSE_NAME -o -r 720 "/path/to/directory/"

***Saving download links***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd https://www.udemy.com/COURSE_NAME -s

***Saving specific resolution download links***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd https://www.udemy.com/COURSE_NAME -s -r 720

***Saving download links to specific location***
	
	python udemy-dl.py -u user@domain.com -p p4ssw0rd https://www.udemy.com/COURSE_NAME -s -o "/path/to/directory/"
	
***Saving specific resolution download links to specific location***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd https://www.udemy.com/COURSE_NAME -s -r 720 -o "/path/to/directory/"

***Listing course's video informtion***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd https://www.udemy.com/COURSE_NAME -l
the above command will list down the size of video and attached files and available resolutions for a video in a course.

### Advanced Usage

<pre><code>
Author: Nasir khan (<a href="http://r0oth3x49.herokuapp.com/">r0ot h3x49</a>)

Usage: udemy-dl.py [-h] [-u "username"] [-p "password"] COURSE_URL
                   [-s] [-l] [-r VIDEO_QUALITY] [-o OUTPUT]

A cross-platform python based utility to download courses from udemy for
personal offline use.

Options:
  General:
    -h, --help        Shows the help.
    -v, --version     Shows the version.

  Advance:
    -u, --username    Username in udemy.
    -p, --password    Password of your account.
    -s, --save-links  Do not download but save links to a file.
    -l, --list-infos  List all lectures with available resolution.
    -r, --resolution  Download video resolution, default resolution is 720p.
    -o, --output      Output directory where the videos will be saved, default
                      is current directory.
  
  Example:
	python udemy-dl.py -u user@domain.com -p P45sw0rd https://www.udemy.com/course_name/
</code></pre>


### Note 
<pre><code>Do not change the position of any argument as given under the Usage, this may cause an error or failur in downloading of course.</code></pre>
