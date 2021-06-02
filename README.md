[![GitHub release](https://img.shields.io/badge/release-v1.1-brightgreen?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/releases/tag/v1.0)
[![GitHub stars](https://img.shields.io/github/stars/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/network)
[![GitHub issues](https://img.shields.io/github/issues/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/issues)
[![GitHub license](https://img.shields.io/github/license/r0oth3x49/udemy-dl.svg?style=flat-square)](https://github.com/r0oth3x49/udemy-dl/blob/master/LICENSE)

# **udemy-dl**

**A cross-platform python based utility to download courses from Udemy.com for personal offline use.**

[![udemy-dl-v1-1.png](https://i.postimg.cc/X7QpzY8q/udemy-dl-v1-1.png)](https://postimg.cc/zVHzL54Y)

| Important Notes ||
|----|--------|
| **Credentials** | Don't share your credentials until the issue is properly tagged/labeled with **account-needed**. |
| **Disclaimer** | Owner of this repository is not responsible for any misuse if you share your credentials with strangers. |

## Usage

### Requirements

- Python 3 only (`Now udemy-dl doesn't support python 2`)
- Python `pip`
- Python module `requests`
- Python module `colorama`
- Python module `unidecode`
- Python module `six`
- Python module `cloudscraper`
- Python module `requests[security]` or `pyOpenSSL`
- FFmpeg (to download hls based streams properly)

### Module Installation

```bash
pip install -r requirements.txt
```

### HLS streams download requirements

- You would need FFmpeg to be installed and added to environment variable so that udemy-dl can access.
- Download [FFmpeg](https://ffmpeg.org/download.html)
  * Note: if you plan on using the multi-course downloader script, it will install ffmpeg automatically.
- On Ubuntu you can install it via `apt install ffmpeg`, and on a Mac with `brew install ffmpeg`
- Add to environment variables then udemy-dl will be able to use it when downloading HLS streams.
  
### Tested on

- Windows 7/8/8.1/10
- Ubuntu-LTS (tested with super user)
- Mac OS-X BigSur 

## Features

- Added proper session management.
- Resume capability for a course video.
- Added proper logging errors and warnings.
- Support multiple courses download from file.
- Supports organization and individual udemy users both.
- Added support to download hls based streams if available.
- Added functionality to reset lecture number to start from 1.
- Added switch for session caching on demand. (option: `--cache`)
- Convert WebVTT to SRT but donot delete WebVTT. (option: `--keep-vtt`)
- Skip fetching HLS streams, This will make the fetching fast. (option: `--skip-hls`)
- List down course contents and video resolution, suggest the best resolution (option: `--info`).
- Download/skip all available subtitles for a video (options: `--sub-only, --skip-sub`).
- Download/skip all available assets for a video (options: `--assets-only, --skip-assets`).
- Download specific chapter in a course (option: `-c / --chapter`).
- Download specific lecture in a chapter (option: `-l / --lecture`).
- Download specific subtitle for a lecture (option: `-s / --sub-lang`).
- Download chapter(s) by providing range in a course (option: `--chapter-start, --chapter-end`).
- Download lecture(s) by providing range in a chapter (option: `--lecture-start, --lecture-end`).
- Download lecture(s) in requested resolution (option: `-q / --quality`).
- Download course to user requested path (option: `-o / --output`).
- Authentication using cookies (option: `-k / --cookies`).

## How to login with cookie

The `cookies.txt` file should have the following simple format, eg:

```ini
access_token=JKU9QNs2IQDBKoYKvOBclSPXN97baf32o1Jo2L9vX
```

### Finding your access token value

To get the cookie value, inspect the page, find the cookies for udemy.com domain, and grab the value of `access_token` cookie.

#### Finding your access token value by Browser

 - Firefox users : [guide by @01ttouch](https://github.com/r0oth3x49/udemy-dl/issues/389#issuecomment-491903900)
 - Chrome users : [guide by @01ttouch](https://github.com/r0oth3x49/udemy-dl/issues/389#issuecomment-492569372)
 
## Usage

### Download udemy-dl

You can download the latest version of udemy-dl by cloning the GitHub repository.

    git clone https://github.com/r0oth3x49/udemy-dl.git

### Examples

Download a course

```bash
python udemy-dl.py COURSE_URL
```

Download a courses from file

```bash
python udemy-dl.py FILE-CONTAINING-COURSE-URLs
```

Download course with specific resolution

```bash
python udemy-dl.py COURSE_URL -q 720
```
  
Download course to a specific location

```bash
python udemy-dl.py COURSE_URL -o "/path/to/directory/"
```

Download course with specific resolution to a specific location

```bash
python udemy-dl.py COURSE_URL -q 720 -o "/path/to/directory/"
```

Download specific chapter from a course

```bash
python udemy-dl.py COURSE_URL -c NUMBER
```

Download specific lecture from a chapter

```bash
python udemy-dl.py COURSE_URL -c NUMBER -l NUMBER
```

Download lecture(s) range from a specific chapter

```bash
python udemy-dl.py COURSE_URL -c NUMBER --lecture-start NUMBER --lecture-end NUMBER
```

Download chapter(s) range from a course

```bash
python udemy-dl.py COURSE_URL --chapter-start NUMBER --chapter-end NUMBER
```

Download specific lecture from chapter(s) range

```bash
python udemy-dl.py COURSE_URL \
    --chapter-start NUMBER \
    --chapter-end NUMBER \
    --lecture NUMBER
```

Download lecture(s) range from chapter(s) range

```bash
python udemy-dl.py  COURSE_URL \
    --chapter-start NUMBER \
    --chapter-end   NUMBER \
    --lecture-start NUMBER \
    --lecture-end   NUMBER
```

List down specific chapter from a course

    python udemy-dl.py COURSE_URL -c NUMBER --info

List down specific lecture from a chapter

    python udemy-dl.py COURSE_URL -c NUMBER -l NUMBER --info

Substitute the language code such as (en, es) if lang switch is not specified then default will be all subtitles

    python udemy-dl.py COURSE_URL --sub-lang en

---

# Downloading Multiple Courses at Once

A recently contributed shell script [`download.sh`](download.sh) is capable of downloading multiple courses, one after another, as to not exceed API request limits, provided the following file exists: `courses.toml`:

```toml
[todo]
url="https://www.udemy.com/course/ableton-live-11-masterclass"
url="https://www.udemy.com/course/ableton-push-workflow-and-production"
url="https://www.udemy.com/course/ableton-live-11-course"

[done]
url="https://www.udemy.com/course/the-complete-internet-security-privacy-course-volume-1"
url="https://www.udemy.com/course/the-easy-beginner-drum-course"
```

You don't need to have any URLs in the `[done]` section, but you must keep the `[done]` section header. The script grabs all URLs between `[todo]` and `[done]`

In addition, the script:

 * Downloads it's own BASH dependency — the [Bashmatic](https://github.com/kigster/bashmatic) library and install it in `~/.bashmatic`
 * Installs `python3.9` if not there
 * Verify that `pip` is a valid command, and remove the symlink if it's not (eg,points to a non-existent python distribution)
 * Installs `pip` if not there
 * Run `pip install -r requirements.txt`
  
## Usage

To download multiple courses serially, follow these steps:

1. create the file `courses.toml` of the format described above and below (also, see [courses-example.toml](./courses-example.toml) file).
2. create the file `cookies.txt` of the format `access_token=XXX` where `XXX` is your access token cookie (see above for how to get it).
3. choose the output directory, or use the default folder: `~/Courses` which will be auto-created.
4. Run the script as follows:

```bash
./download.sh <courses-toml> [ optional-download-folder ]
```

For instance:

#### Define which courses to download:

```toml
cat <<EOF > courses.toml
[todo]
url="https://www.udemy.com/course/ableton-live-11-masterclass"
url="https://www.udemy.com/course/ableton-push-workflow-and-production"
url="https://www.udemy.com/course/ableton-live-11-course"
[done]
EOF
```

NOTE: The script does not modify your TOML file; for the courses that downloaded without errors, you might want to move them to the `[done]` section, so that they won't be re-downloaded by accident.

#### Setup your access token

Login to Udemy in Chrome, press Cmd-Option-I to start developer tools, and grab the value of the  `access_token` cookie, and we'll save it to `cookies.txt`:

```bash
echo 'access_token=8M75pMO0F7zaoZu2lFWxazKPKutMQKCm568wIsjA' > cookies.txt
```

#### Specify the download directory 

The script will read any environment overrides from a file in the current directory called `.envrc.local` — we can use this file to set the target download directory as a `DOWNLOAD_DIR` variable.


```bash
echo 'export DOWNLOAD_DIR="${HOME}/Documents/Courses"' > .envrc.local
./download.sh courses.toml
```

Alternatively, you can pass the download folder as the second argument to the `download.sh` script:

```bash
./download.sh courses.toml ~/Documents/Courses
```

Finally, you can just set this variable before running the script:

```bash
DOWNLOAD_DIR=${HOME}/Documents ./download.sh courses.toml
```

## Experimental Features

### Downloading Multiple Courses at the Same Time

Set environment variable:

```bash
export DOWNLOAD_CONCURRENTLY=1 
./download.sh courses.toml
```

Try this at your own risk. But, if this works — and you have 20+ courses, it will go a LOT faster.

### Saving Course Info 

Set environment variable:

```bash
export DOWNLOAD_INFO=1 
./download.sh course.toml
```

This invokes `udemy-dl` twice: once with `--info` and on the background, and the other for the actual content. 

You should have a file "course-name.info.txt" in the download directory, with the output of the `--info` command.

### Both Options Together

```bash
export DOWNLOAD_CONCURRENTLY=1 
export DOWNLOAD_INFO=1 
./download.sh course.toml ~/Documents/Courses
```

NOTE: **when running downloads concurrently, the script will wait for all background jobs to finish before exiting.**

## Appendix

### `udemy-dl.py` Help Screen


```bash
$ python3.9 udemy-dl.py -h


              __                               ____
   __  ______/ /__  ____ ___  __  __      ____/ / /
  / / / / __  / _ \/ __ `__ \/ / / /_____/ __  / /
 / /_/ / /_/ /  __/ / / / / / /_/ /_____/ /_/ / /
 \__,_/\__,_/\___/_/ /_/ /_/\__, /      \__,_/_/
                           /____/
                                 Version : 1.1
                                 Author  : Nasir Khan (r0ot h3x49)
                                 Github  : https://github.com/r0oth3x49

usage: udemy-dl.py [-h] [-v] [-u] [-p] [-k] [-o] [-q] [-c] [-l] [-s] 
                   [--chapter-start] [--chapter-end] [--lecture-start] 
                   [--lecture-end] [--info] [--cache] [--keep-vtt]
                   [--sub-only] [--skip-sub] [--skip-hls] [--assets-only] [--skip-assets]
                   course

A cross-platform python based utility to download courses from udemy for personal offline use.

positional arguments:
  course            Udemy course or file containing list of course URL(s).

General:
  -h, --help        Shows the help.
  -v, --version     Shows the version.

Authentication:
  -u , --username   Username in udemy.
  -p , --password   Password of your account.
  -k , --cookies    Cookies to authenticate with.

Advance:
  -o , --output     Download to specific directory.
  -q , --quality    Download specific video quality.
  -c , --chapter    Download specific chapter from course.
  -l , --lecture    Download specific lecture from chapter(s).
  -s , --sub-lang   Download specific subtitle/caption (e.g:- en).
  --chapter-start   Download from specific position within course.
  --chapter-end     Download till specific position within course.
  --lecture-start   Download from specific position within chapter(s).
  --lecture-end     Download till specific position within chapter(s).

Others:
  --info            List all lectures with available resolution.
  --cache           Cache your session to avoid providing again.
  --keep-vtt        Keep WebVTT caption(s).
  --sub-only        Download captions/subtitle only.
  --skip-sub        Download course but skip captions/subtitle.
  --skip-hls        Download course but skip hls streams. (fast fetching).
  --assets-only     Download asset(s) only.
  --skip-assets     Download course but skip asset(s).
```

# Contributing

## Before creating an issue, please do the following:

 1. **Use the GitHub issue search** &mdash; check if the issue is already reported.
 2. **Check if the issue is already fixed** &mdash; try to reproduce it using the latest `master` in the repository.
 3. Make sure, that information you are about to report is related to this repository and not the one available on Python's repository, PyPi, Because this repository cannot be downloaded/installed via pip command.
 4. Follow issue reporting template properly otherwise the issue will be closed.

## Todo

 - Add support to download course on a flaky connection.
