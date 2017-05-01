#!/usr/bin/python
# -*- coding: utf-8 -*-


from sys import *
from requests import get
from pprint import pprint
from udemy.colorized import *
import udemy,os,time,optparse
from udemy.colorized.banner import banner


extract_info = udemy.UdemyInfoExtractor()
course_dl = udemy.Downloader()

class UdemyDownload:

    def __init__(self, url, username, password, list_down=False, save_links=False, outto=None, quality=None):
        self.url        = url
        self.username   = username
        self.password   = password
        self.list       = list_down
        self.save       = save_links
        self.outto      = outto
        self.quality    = quality
        


    def login(self):
        extract_info.login(self.username, self.password)

    def logout(self):
        extract_info.logout()

    def Progress(self, iteration, total, prefix = '' , fileSize='' , downloaded = '' , rate = '' ,suffix = '', barLength = 100):
        filledLength    = int(round(barLength * iteration / float(total)))
        percents        = format(100.00 * (iteration / float(total)), '.2f')
        bar             = fc + sd + ('█' if os.name == 'posix' else '#') * filledLength + fg + sd +'-' * (barLength - filledLength)
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + str(fileSize) + '/' + str(downloaded) + ' ' + percents + '% |' + bar + fg + sb + '| ' + str(rate) + ' ' + str(suffix) + 's ETA                                      \r')
        stdout.flush()

    def Download(self, total, recvd, ratio, rate, eta):
        TotalSize = round(float(total) / 1048576, 2)
        Receiving = round(float(recvd) / 1048576, 2)
        Size = format(TotalSize if TotalSize < 1024.00 else TotalSize/1024.00, '.2f')
        Received = format(Receiving if Receiving < 1024.00 else Receiving/1024.00,'.2f')
        SGb_SMb = 'MB' if TotalSize < 1024.00 else 'GB'
        RGb_RMb = 'MB ' if Receiving < 1024.00 else 'GB '
        Dl_Speed = round(float(rate) , 2)
        dls = format(Dl_Speed if Dl_Speed < 1024.00 else Dl_Speed/1024.00, '.2f')
        Mb_kB = 'kB/s ' if Dl_Speed < 1024.00 else 'MB/s '
        (mins, secs) = divmod(eta, 60)
        (hours, mins) = divmod(mins, 60)
        if hours > 99:
            eta = "--:--:--"
        if hours == 0:
            eta = "%02d:%02d" % (mins, secs)
        else:
            eta = "%02d:%02d:%02d" % (hours, mins, secs)
        self.Progress(Receiving, TotalSize, fileSize = str(Size) + str(SGb_SMb) , downloaded = str(Received) + str(RGb_RMb), rate = str(dls) + str(Mb_kB), suffix = str(eta), barLength = 40)

    def Downloader(self, url, title, path):
        out = course_dl.download(url, title, filepath=path, quiet=True, callback=self.Download)
        if 'EXISTS' in out:
            return 'already_exist'
        elif out == '401':
            stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Udemy Says (HTTP Error 401 : Unauthorized)\n")
            stdout.write(fc + sd + "[" + fw + sb + "*" + fc + sd + "] : " + fw + sd + "Try to run the udemy-dl again...\n")
            exit(0)
            
    def SaveLinks(self, path=None):
        if not path:
            current_dir = os.getcwd()
        else:
            if os.path.exists(path):
                current_dir = path
                os.chdir(current_dir)
            else:
                current_dir = os.getcwd()
                stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Path '%s' does not exist, saving to '%s'" % (path, current_dir))
                
        stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading webpage..\n")
        time.sleep(2)
        course_path = extract_info.match_id(self.url)
        course      = "%s" % (course_path) 
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Extracting course information..\n")
        time.sleep(2)
        course_name = current_dir + '\\' + course_path if os.name == 'nt' else current_dir + '/' + course_path
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading " + fb + sb + "'%s'.\n" % (course.replace('-',' ')))
        self.login()
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading course information webpages ..\n")
        videos_dict = extract_info.real_extract(self.url, course_name, course_path)
        self.logout()
        if isinstance(videos_dict, dict):
            if os.name == 'nt':
                stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Saving links under '%s\\%s.txt'\n" % (current_dir, course))
            else:
                stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Saving links under '%s/%s.txt'\n" % (current_dir, course))
            for chap in sorted(videos_dict):
                for lecture,dl_links in sorted(videos_dict[chap].iteritems()):
                    hd =  max(dl_links)
                    for kay,value in hd.iteritems():
                        hdVideo = value
                    if hdVideo:
                        with open("%s.txt" % (course), "a") as f:
                            f.write("%s\n%s\n" % (lecture, hdVideo))
                            f.close()
            stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Saved successfully.\n")
                            
                            
    def get_filsize(self, url):
        req = get(url, stream=True)
        size = round(float(req.headers.get('Content-Length')) / 1048576, 2)
        sz = size if size < 1024.00 else round(size/1024.00,2)
        in_MB = "MB " if size < 1024.00 else 'GB '
        return sz,in_MB
            
    def ListDown(self):
        current_dir = os.getcwd()
        stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading webpage..\n")
        time.sleep(2)
        course_path = extract_info.match_id(self.url)
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Extracting course information..\n")
        time.sleep(2)
        course_name = current_dir + '\\' + course_path if os.name == 'nt' else current_dir + '/' + course_path
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading " + fb + sb + "'%s'.\n" % (course_path.replace('-',' ')))
        self.login()
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading course information webpages ..\n")
        videos_dict = extract_info.real_extract(self.url, course_name, course_path)
        self.logout()
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Extracting chapters & lectures information..\n")
        if isinstance(videos_dict, dict):
            for chap in sorted(videos_dict):
                stdout.write(fc + sd + "\n[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)\n" % (chap))
                for lecture,dl_links in sorted(videos_dict[chap].iteritems()):
                    stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fy + sb + "Lecture '" + fm + sd + str(lecture)+ fy + sb + "'..")
                    stdout.write(fy + sb + "\n+--------------------------------------------------------+\n")
                    stdout.write(fy + sb + "|     {:<6} {:<8} {:<7} {:<12} {:<14}|\n".format("Stream", "Type", "Format", "Quality", "Size"))
                    stdout.write(fy + sb + "|     {:<6} {:<8} {:<7} {:<10} {:<16}|\n".format("------", "-----", "------", "-------", "--------"))
                    itr = len(dl_links)
                    for i in range(0, itr):
                        sid         = i + 1
                        quality     = dl_links[i].keys()[0]
                        url         = dl_links[i].get(quality)
                        sz,in_MB    = self.get_filsize(url)
                        media       = 'video'
                        Format      = 'mp4'
                        stdout.write(fy + sb + "|" + fg + sd + "     {:<6} {:<8} {:<7} {:<10} {:<7}{:<9}{}{}|\n".format(sid, media, Format , str(quality) + 'p', sz, in_MB, fy, sb))
                    stdout.write(fy + sb + "+--------------------------------------------------------+\n")

        
    def ExtractAndDownload(self, path=None, quality=None):
        current_dir = os.getcwd()
        stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading webpage..\n")
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Extracting course information..\n")
        time.sleep(2)
        course = extract_info.match_id(self.url)
        if not path:
            course_path = extract_info.match_id(self.url)
            course_name = current_dir + '\\' + course_path if os.name == 'nt' else current_dir + '/' + course_path
        else:
            course_path = "%s\\%s" % (path, extract_info.match_id(self.url)) if os.name == 'nt' else "%s/%s" % (path, extract_info.match_id(self.url))
            course_name = course_path
            
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading " + fb + sb + "'%s'.\n" % (course.replace('-',' ')))
        self.login()
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading course information webpages ..\n")
        videos_dict = extract_info.real_extract(self.url, course_name, course_path)
        self.logout()
        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Counting no of chapters..\n")
        time.sleep(0.5)
        if isinstance(videos_dict, dict):
            stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fw + sd + "Found ('%s') chapter(s).\n" % (len(videos_dict)))
            j = 1
            for chap in sorted(videos_dict):
                stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fm + sb + "Downloading chapter : (%s of %s)\n" % (j, len(videos_dict)))
                stdout.write(fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)\n" % (chap))
                chapter_path = course_path + '\\' + chap if os.name == 'nt' else course_path + '/' + chap
                try:
                    os.makedirs(chapter_path)
                except  Exception as e:
                    pass
                chapter_path = course_name + '\\' + chap if os.name == 'nt' else course_name + '/' + chap
                if os.path.exists(chapter_path):
                    os.chdir(chapter_path)
                stdout.write(fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fc + sd + "Found ('%s') lecture(s).\n" % (len(videos_dict[chap])))
                i = 1
                for lecture_name, dl_links in sorted(videos_dict[chap].iteritems()):
                    if not quality:
                        hd =  max(dl_links)
                        for kay,value in hd.iteritems():
                            hdVideo = value
                    else:
                        found = False
                        itr = len(dl_links)
                        for i in range(0, itr):
                            res     = dl_links[i].keys()[0]
                            if res == quality:
                                hdVideo = dl_links[i].get(res)
                                found = True
                            else:
                                continue
                        if not found:
                            stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Request quality is not available for (%s)\n" % (lecture_name))
                            askUser = raw_input(fc + sd + "[" + fw + sb + "?" + fc + sd + "] : " + fw + sb + "Would you like to download the default quality (y/n) : ")
                            if askUser == 'y' or askUser == 'Y' or askUser == '':
                                hd =  max(dl_links)
                                for kay,value in hd.iteritems():
                                    hdVideo = value
                            else:
                                i += 1
                                stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Continuing to check for the next lecture..\n")
                                continue
                    if hdVideo:
                        stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading lecture : (%s of %s)\n" % (i, len(videos_dict[chap])))
                        stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)\n" % (lecture_name))
                        out = self.Downloader(hdVideo, lecture_name, chapter_path)
                        if out == 'already_exist':
                            stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % (lecture_name) + fy + sb + "(already downloaded).\n")
                        else:
                            stdout.write(fc + sd + "\n[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)\n" % (lecture_name))
                        i += 1
                j += 1
                stdout.write('\n')
                os.chdir(current_dir)

def main():
    stdout.write(banner())
    us = '''%prog [-h] [-u "username"] [-p "password"] COURSE_URL
                   [-s] [-l] [-o OUTPUT] [-r VIDEO_QUALITY]'''
    version = "%prog version 0.1"
    parser = optparse.OptionParser(usage=us,version=version,conflict_handler="resolve")

    general = optparse.OptionGroup(parser, 'General')
    general.add_option(
        '-h', '--help',
        action='help',
        help='Shows the help.')
    general.add_option(
        '-v', '--version',
        action='version',
    help='Shows the version.')

    downloader = optparse.OptionGroup(parser, "Advance")
    downloader.add_option(
        "-u", "--username", 
        action='store_true',
        dest='email',\
        help="Username in udemy.")
    downloader.add_option(
        "-p", "--password", 
        action='store_true',
        dest='password',\
        help="Password of your account.")
    downloader.add_option(
        "-s", "--save-links", 
        action='store_true',
        dest='save_links',\
        help="Do not download but save links to a file.")
    downloader.add_option(
        "-l", "--list-infos", 
        action='store_true',
        dest='list',\
        help="Just list all lectures and their name with resolution.")
    downloader.add_option(
        "-r", "--resolution", 
        action='store_true',
        dest='quality',\
        help="Download video resolution, default resolution is 720p.")
    downloader.add_option(
        "-o", "--output", 
        action='store_true',
        dest='output',\
        help="Output directory where the videos will be saved, default is current directory.")

    parser.add_option_group(general)
    parser.add_option_group(downloader)

    (options, args) = parser.parse_args()

    if not options.email and not options.password:
        parser.print_help()

    elif options.email and options.password and not options.save_links and not options.list and not options.output and not options.quality:
        email   = args[0]
        passwd  = args[1]
        url     = args[2]
        udemy =  UdemyDownload(url, email, passwd)
        udemy.ExtractAndDownload()
    elif options.email and options.password and options.save_links and not options.list and not options.output and not options.quality:
        email   = args[0]
        passwd  = args[1]
        url     = args[2] if 'http' in args[2] else args[3]
        links   = options.save_links
        udemy   =  UdemyDownload(url, email, passwd)
        udemy.SaveLinks()
    elif options.email and options.password and options.save_links and not options.list and options.output and not options.quality:
        email   = args[0]
        passwd  = args[1]
        url     = args[2]
        outto   = args[3]
        links   = options.save_links
        udemy   =  UdemyDownload(url, email, passwd)
        udemy.SaveLinks(path=outto)
    elif options.email and options.password and not options.save_links and options.list and not options.output and not options.quality:
        email   = args[0]
        passwd  = args[1]
        url     = args[2] if 'http' in args[2] else args[3]
        lists   = options.list
        udemy   =  UdemyDownload(url, email, passwd)
        udemy.ListDown()
    elif options.email and options.password and not options.save_links and not options.list and options.output and not options.quality:
        email   = args[0]
        passwd  = args[1]
        url     = args[2] 
        outto   = args[3] 
        udemy   =  UdemyDownload(url, email, passwd)
        udemy.ExtractAndDownload(path=outto)
    elif options.email and options.password and not options.save_links and not options.list and options.output and options.quality:
        email   = args[0]
        passwd  = args[1]
        url     = args[2]
        res     = args[3]
        outto   = args[4]
        udemy =  UdemyDownload(url, email, passwd)
        udemy.ExtractAndDownload(path=outto, quality=res)
    elif options.email and options.password and not options.save_links and not options.list and not options.output and options.quality:
        email   = args[0]
        passwd  = args[1]
        url     = args[2]
        res     = args[3]
        udemy =  UdemyDownload(url, email, passwd)
        udemy.ExtractAndDownload(quality=res)
    else:
        parser.print_help()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        stdout.write(fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..")
        time.sleep(0.8)
    except IndexError:
        stdout.write(fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "Required fields seems empty please fill with proper input of username,password and course url..")

        
        
