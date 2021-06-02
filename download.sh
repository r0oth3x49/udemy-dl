#!/usr/bin/env bash
# vim: ft=bash
# 
# udemy-dl is © Nasir Khan @r0oth3x49 on Github
# download.sh and Bashmatic are © 2021 Konstantin Gredeskoul, @kigster on Github
#
# How to run this script:
#
#    We recommend running it in the udemy-dl project folder, otherwise you must add the
#    folder to the $PATH variable. Just create courses.toml and cookies.txt (gitignored)
#    locally and run it like so:
#
#    $ DOWNLOAD_INFO=1 DOWNLOAD_DIR=~/Desktop ./download.sh courses.toml 
#

# These can be overridden by setting them before running the script.
export DOWNLOAD_DIR="${DOWNLOAD_DIR:-${DEFAULT_DOWNLOAD_DIR}}"
export DOWNLOAD_QUALITY="${DOWNLOAD_QUALITY:-"1080"}"
export DOWNLOAD_CONCURRENTLY=${DOWNLOAD_CONCURRENTLY:-"0"} # when set to 1, each course is downloaded in a separate Python process.
export DOWNLOAD_INFO=${DOWNLOAD_INFO:-"0"} # when set to 1, download --info for the course into the course-file-info.txt file.

# These are not to be modified by the user.
export PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")"; pwd -P)
export DEFAULT_DOWNLOAD_DIR="${HOME}/Documents/Courses"
declare -a REQUIRED_PACKAGES
export REQUIRED_PACKAGES=(ffmpeg)

function download.bashmatic() {
  [[ -z ${BASHMATIC_HOME} ]] && export BASHMATIC_HOME="${HOME}/.bashmatic"
  [[ -d ${BASHMATIC_HOME} ]] || bash -c "$(curl -fsSL https://bashmatic.re1.re); bashmatic-install -q"
  [[ -d ${BASHMATIC_HOME} ]] || {
    echo "Can't find Bashmatic, even after attempting an installation."
    echo "Please install Bashmatic with the following command line:"
    # shellcheck disable=SC2016
    echo 'bash -c "$(curl -fsSL https://bashmatic.re1.re); bashmatic-install"'
    exit 1
  }

  # shellcheck disable=SC1090
  . "${BASHMATIC_HOME}"/init.sh  
}

export install_command

function install.local.packages() {
  local -a install_commands
  case "${BASHMATIC_OS}" in
    "darwin") 
      install_commands+=("brew install $*")
      ;;
    "linux")
      local packages="$*"
      packages="$(echo "${packages}" | tr -d '@')"
      local sudo="sudo "
      [[ ${USER} == "root" ]] && sudo=""
      install_commands+=( "${sudo} apt-get update -yq" )
      install_commands+=( "${sudo} apt-get install -yq ${packages}" )
      ;;
    *)
      error "Operating system ${BASHMATIC_OS} is not supported."
      exit 1
  esac

  [[ ${install_commands[*]} =~ sudo ]] && {
    info "You may be asked for your SUDO password in the next step."
    info "Please enter it now:"
    sudo echo -n
  }

  for command in "${install_commands[@]}"; do
    run "${command}"
  done
}

function download.dependencies() {
  install.local.packages "${REQUIRED_PACKAGES[@]}"
}

function download.python() {
  local python
  for version in 3  3.9  3.8  3.7 ; do
    command -v "python${version}" >/dev/null && {
      p=$(command -v "python${version}")
      printf -- "%s" "$p"
      return 0
    }
  done

  if [[ -z $python ]] ; then
    warning "Couldn't find Python3, attempting to install..." >&2
    install.local.packages "python@3.9" >&2
    python=$(command -v python3.9 || command -v python3) >&2
  fi
  
  [[ -z $python ]] && {
    error "Unable to find and install Python Interpreter" \
          "Please attempt to install python3.9 manually and retry." >&2
    exit 1
  }

  printf -- "%s" "${python}"
}

function download.pip() {
  command -v pip >/dev/null && {
     pip --help 2>/dev/null 1>&2 || {
       code=$?
       [[ ${code} -eq 126 ]] && run "rm -f $(command -v pip)"
     }
  }

  run "hash -r"

  command -v pip >/dev/null || {
    info "No pip found, downloading it ..."
    run "curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
    run "${python} get-pip.py"
  }
  run "pip install -r requirements.txt"
}

function download.course() {
  local url="$1"
  local folder="${2:-${DOWNLOAD_DIR}}"

  [[ -z "$url" ]] && {
    error "No URL provided, aborting."
    return 1
  }
  
  local course
  course="$(basename "${url}")"
  [[ -d "${folder}" ]] || run "mkdir -p ${folder}"

  h3 "Downloading Lectures" "URL: ${bldylw}${url}" "–—>: ${bldred}${folder}"
 
  ((DOWNLOAD_INFO)) && {
    local info_file="${folder}/${course}.info.txt"

    info "First, downloading info for course ${course} into the file:"
    info "${bldylw}${info_file}"

    local background=""
    ((DOWNLOAD_CONCURRENTLY)) && background=" & "

    [[ -n $DEBUG ]] && set -xe
    eval "${PYTHON} udemy-dl.py \"${url}\" \
        -k cookies.txt --info 1>\"${info_file}\" 2>&1 ${background}"
    set +xe

    h "Course ${course} info is downloading into ${info_file}..."
  }

  if ((DOWNLOAD_CONCURRENTLY)); then
    local log="${folder}/${course}.concurrent.log"
    [[ -n $DEBUG ]] && set -xe
    ${PYTHON} udemy-dl.py "${url}" -q "${DOWNLOAD_QUALITY}" \
        -k cookies.txt --sub-lang en --cache -o "${folder}" 1>"${log}" 2>&1 &
    local code=$? 
    set +xe

    h2 "Course download has begun on the background. " \
     "To see it's output: "\
     "  > ${bldylw}tail -f ${log}" \
     " " \
     "Or to see all the logs at the same time: " \
     "  > ${bldylw}tail -f ${folder}/*.concurrent.log"

  else
    # Explicit output, serialized order
    [[ -n $DEBUG ]] && set -xe
    local log="${folder}/${course}.serial.log"
    ${PYTHON} udemy-dl.py "${url}" -q "${DOWNLOAD_QUALITY}" \
        -k cookies.txt --sub-lang en --cache -o "${folder}" 2>&1 | tee -a "${log}"
    local code=$? 
    set +xe
  fi
  ((code)) && {
    error "Error downloading course ${course}"
    exit 2
  }
}

h() { 
  arrow.blk-on-ylw "$@"
}

function courses.todo() {
  local file="$1"
  sed -E -n '/\[todo\]/,/\[done\]/P' "${file}" | awk 'BEGIN{FS="="}{if ($1=="url") { print $2 }}' | tr -d '"'
}

# Use this to override DOWNLOAD_DIR or do additional steps, like mount an external drive
function load.local-env() {
  [[ -f .envrc.local ]] || return 0

  h 'Loading localized environmen from .envrc.local'
  # shellcheck disable=SC1091
  [[ -f .envrc.local ]] && source ".envrc.local"
}

function download.main() {
  local toml="${1}"; shift
  
  load.local-env

  local folder="${1:-${DOWNLOAD_DIR}}"
  local python
  set +xe
  unset DEBUG

  h 'Looking for python3...'
  python="$(download.python)"
  [[ -x ${python} && $(${python} --version) =~ "Python" ]] || {
    error "Unable to get an valid Python Interpreter." \
     "Got this: ${python}"
    return 1
  }

  export PYTHON="${python}"

  h 'Looking for pip...'
  download.pip

  h "Looking for additional dependencies $(array.to.csv "${REQUIRED_PACKAGES[@]}")"
  download.dependencies

  [[ -f cookies.txt ]] || {
    error "ERROR: cookies.txt is missing.  You must login to udemy.com and grab your ${bldylw}access_token" \
     "For instructions on how to do this in Chrome, click on the following link:"\
     "${undblu}https://github.com/r0oth3x49/udemy-dl/issues/389#issuecomment-492569372"
    return 1
  }

  declare -a course_names
  # shellcheck disable=SC2207
  declare -a course_urls=($(courses.todo "${toml}"))
  for course in "${course_urls[@]}"; do
    course_names+=( "   • ${bldpur}$(basename ${course})" )
  done
  h1bg "About to begin downloading of ${#course_urls[@]} courses using udemy-dl ©  "\
     "Download Directory  : ${bldylw}${folder}" \
     "Access Token Cookie : ${bldylw}$(cat cookies.txt | sed 's/access_token=//g' | tr -d '\n')" \
     "List of Courses     : " \
     "${course_names[@]}"

  info "Depending on the number of courses your download may take a while."
  run.ui.ask "Continue with the download?"

  for course in "${course_urls[@]}"; do
    hr; echo
    h3 "Course: ${bldred}$(printf "%-50s" "${course}")"
    download.course "${course}" "${folder}"
  done

  concurrent.wait 
}

function concurrent.wait {
  # this waits for all jobs and returns the exit code of the last failing job
  ecode=0

  while true; do
      [ -z "$(jobs)" ] && break
      wait -n
      err="$?"
      [ "$err" != "0" ] && ecode="$err"
  done
  return $ecode
}

function main() {
  download.bashmatic
  output.constrain-screen-width 90
  [[ -z "$*" ]] && {
    usage-box "$0 <courses.toml> [ output-folder ] © Multi-course downloadedr based on udemy-dl Python Script" \
      " " " " \
      "courses.toml" "Must be in the TOML format, " \
      " " "url=\"...\" listed between [todo] and [done]" \
      "output folder" "Top level folder under which each course folder will be created." \
      "cookies.txt" "Must be present in the current folder and be of the format" \
      " " "${bldylw}access_token=${bldgrn}FFDFD1123441fF9F78789874185128597${clr}"
    return 1
  }

  [[ "$1" =~ .toml$ ]] || {
    error "First argument should be a TOML file"
    return 1
  }

  trap 'exit 111' INT
  download.main "$@"
}

main "$@"


