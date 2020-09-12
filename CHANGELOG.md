# Change Log

## 1.0 (2020-09-12)

Features:
  - Added proper session management.
  - Restructure code to make it bit nicer.
  - Added proper logging for errors and warning which fixes (#477).
  - Added support to download multiple courses from file.
  - Added support to download by default just EN subtitle. (could use `--sub-lang` to download others)
  - Added switch to keep WebVTT subtitles (option: `--keep-vtt`).
  - Added support to fetch/skip HLS streams such as 1080p etc. (option to skip `--skip-hls`).
  - Removed `--names`, `--save` switches.
  - Removed `--cache` switch as proper session management is added.
  - Removed `--unsafe` switch now unicode characters are handled properly in code.
  - Added support to download/skip all available assets for a video (options: `--assets-only, --skip-assets`).

## 0.5 (2018-05-21)

Features:
  - Authentication using cookies thanks to @jhonyyy90 for sharing credentials (option: `-k / --cookies`).
  - Download/save lecture names to file thanks to @serhattsnmz (option: `--names`).
  - Download lectures containing unsafe (`unicode`) characters in title/name thanks to @tofanelli and @Chlitzxer (option: `--unsafe`).

## 0.4 (2018-02-26)

Features:
  - Download spacific chapter in a course (option: `-c / --chapter`) thanks to @alfari16.
  - Download chapter(s) by providing range in a course (option: `--chapter-start, --chapter-end`).
  - Download specific lecture in a chapter (option: `-l / --lecture`).
  - Download lecture(s) by providing range in a chapter (option: `--lecture-start, --lecture-end`).
  - Changed (option: `-l / --list-infos`) by (option: `--info`).
  - Changed (option: `-c / --configs`) by (option: `--cache`).
  - Changed (option: `-s / --save-links`) by (option: `--save`).
  - Changed (option: `-r / --resolution`) by (option: `-q / --quality`).
  - Removed (option: `-d / --get-default`).

## 0.3 (2017-11-14)

Features:
  - Skip captions/subtitle and download course only (option: `--skip-sub`).
  - Download captions/subtitle only thanks to @leo459028 (option: `--sub-only`).
  - Edit the password by pressing backspace on command line.

Bugfixes:
  - Fixed some issues & improved code quality for Python3.
  - Fixed #13 (UnicodeEncodeError) thanks for quick patch by @jdsantiagojr.

## 0.2 (2017-08-29)

Features:
  - Download the default quality if requested quality is not there (option: `-d / --get-default`).
  - Cache the credentials to file and use it later for login purpose (option: `-c / --configs`).
  - Get user input if no credentials provided using command line argument.

Bugfixes:
  - Updated code for downloading captions (subtitles) if available.


## 0.1 (2017-08-01)

Features:
  - Resume capability for a course video.
  - Saves direct download links to a file, If you don't want to download.
  - Downloads all available subtitles if any attached with video.
  - List down all available resolution for a video in a course.
  - Saves course to user provided path (directory), default is current directory.