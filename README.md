[![GitHub release](https://img.shields.io/badge/release-v0.3-brightgreen.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/releases/tag/v0.3)
[![GitHub stars](https://img.shields.io/github/stars/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/network)
[![GitHub issues](https://img.shields.io/github/issues/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/issues)

# udemy-dl
**A cross-platform python based utility to download courses from udemy for personal offline use.**

[![udemy-dl.gif](https://s26.postimg.org/st8y7ud5l/udemy-dl.gif)](https://postimg.org/image/y4nusjz85/)

### Requirements

- Python (2 or 3)
- Python `pip`
- Python module `requests`
- Python module `colorama`
- Python module `unidecode`
- Python module `six`
- Python module `requests[security]` or `pyOpenSSL`

### Install modules

	pip install -r requirements.txt
	
### Tested on

- Windows 7/8/8.1
- Kali linux (2017.2)
- Mac OSX 10.9.5 (tested with super user)
 
### Download udemy-dl

You can download the latest version of udemy-dl by cloning the GitHub repository.

	git clone https://github.com/r0oth3x49/udemy-dl.git
	
### Updates

- Added feature to download the default quality if requested quality is not there.
- Added feature to cache the credentials to file and use it later for login purpose.
- Added feature to get user input if no credentials provided using command line argument.
- Updated code for downloading captions (subtitles) if available.


### Change-log

- Fixed some issues & improved code quality for Python3.
- Fixed #13 (UnicodeEncodeError) thanks for quick patch by @jdsantiagojr 
- Added feature to skip captions/subtitle and download course only.
- Added feature to download captions/subtitle only thanks to @leo459028.
- Added feature to edit the password by pressing backspace on command line.
	
### Configuration

<pre><code>
	
	
	{
		"username" 		: "user@domain.com",
		"password" 		: "p4ssw0rd",
		"output" 		: "path/to/directory/",
		"resolution" 		: "1080"
	}
	
	Example for windows users to set output directory:
		"output" 		: "path\\to\\directory"
		
</code></pre>


### Usage

***Downloading course***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL
	
***Downloading Course with specific resolution***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL -r 720
	
***Downloading course to a specific location***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL -o "/path/to/directory/"
	
***Downloading course with specific resolution to a specific location***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL -r 720 -o "/path/to/directory/"

***Saving download links***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL -s

***Saving specific resolution download links***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL -s -r 720

***Saving download links to specific location***
	
	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL -s -o "/path/to/directory/"
	
***Saving specific resolution download links to specific location***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL -s -r 720 -o "/path/to/directory/"

***Downloading course and caching credentials***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL --configs

***Downloading with specific resolution and allow default resolution as well***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL -r 1080 -d

***Downloading course but skip captions/subtitles***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL --skip-sub

***Downloading captions/subtitles only***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL --sub-only

***Listing course's video informtion***

	python udemy-dl.py -u user@domain.com -p p4ssw0rd COURSE_URL -l
the above command will list down the size of video and attached files and available resolutions for a video in a course.

### Advanced Usage

<pre><code>
Author: Nasir khan (<a href="http://r0oth3x49.herokuapp.com/">r0ot h3x49</a>)

Usage: udemy-dl.py [-h] [-u "username"] [-p "password"] COURSE_URL
                   [-s] [-l] [-r "resolution"] [-o "/path/to/directory/"]
                   [-d] [-c/--configs] [--sub-only] [--skip-sub]

A cross-platform python based utility to download courses from udemy for
personal offline use.

Options:
  General:
    -h, --help         Shows the help.
    -v, --version      Shows the version.

  Advance:
    -u, --username     Username in udemy.
    -p, --password     Password of your account.
    -c, --configs      Cache your credentials to use it later.
    -s, --save-links   Do not download but save links to a file.
    -l, --list-infos   List all lectures with available resolution.
    -r, --resolution   Download video resolution, default resolution is 720p.
    -d, --get-default  Download default resolution if requested not there.
    -o, --output       Output directory where the videos will be saved,
                       default is current directory.
  
  Others:
    --sub-only         Download captions/subtitle only.
    --skip-sub         Download course but skip captions/subtitle.

  Example:
	python udemy-dl.py  COURSE_URL
</code></pre>


### Note 
<pre><code>Do not change the position of any argument as given under the Usage, this may cause an error or failur in downloading of course.</code></pre>
