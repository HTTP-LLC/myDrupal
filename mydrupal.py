#!/usr/bin/python3
import requests
import argparse
import random
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

####################################################################################################################

verbose = False

####################################################################################################################

def get_random_useragent():
  ''' Returns a randomly chosen User-Agent string.
  '''
  win_edge = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
  win_firefox = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/43.0'
  win_chrome = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
  lin_firefox = 'Mozilla/5.0 (X11; Linux i686; rv:30.0) Gecko/20100101 Firefox/42.0'
  mac_chrome = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.38 Safari/537.36'
  ie = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)'
  
  ua_dict = {
    1: win_edge,
    2: win_firefox,
    3: win_chrome,
    4: lin_firefox,
    5: mac_chrome,
    6: ie
  }
  rand_num = random.randrange(1, (len(ua_dict) + 1))
  return ua_dict[rand_num]

####################################################################################################################

def check_version(version):
  cve_2018_7600 = ['7.58', '8.4.6', '8.5.1', 'https://www.drupal.org/sa-core-2018-002']
  cve_2018_7602 = ['7.59', '8.4.8', '8.5.3', 'https://www.drupal.org/sa-core-2018-004']
  vuln_status = ['0', False, False]

  if version[0] == "6":
    vuln_status[0] = '0'
    vuln_status[1] = True
    vuln_status[2] = True
  elif version[0] == "7":
    vuln_status[0] = '1'
    if version < cve_2018_7600[0]:
      vuln_status[1] = True
    if version < cve_2018_7602[0]:
      vuln_status[2] = True
  elif version[0] == "8":
    if version[2] == "4":
      vuln_status[0] = '2'
      if version < cve_2018_7600[1]:
        vuln_status[1] = True
      if version < cve_2018_7602[1]:
        vuln_status[2] = True
    elif version[2] == "5":
      vuln_status[0] = '3'
      if version < cve_2018_7600[2]:
        vuln_status[1] = True
      if version < cve_2018_7602[2]:
        vuln_status[2] = True
  else:
    vuln_status[0] = '-1'
    vuln_status[1] = False
    vuln_status[2] = False

  if vuln_status[1]:
    print("[+] Possibly vulnerable to CVE-2018-7600!")
    if verbose == True:
      print("[+] See " + cve_2018_7600[-1] + " for more information.")
    if args.outfile:
      file.write("[+] Possibly vulnerable to CVE-2018-7600!" + '\n')
      file.write("[+] See " + cve_2018_7600[-1] + " for more information." + '\n')
  else:
    print("[-] Not vulnerable to CVE-2018-7600!")
    if args.outfile:
      file.write("[-] Not vulnerable to CVE-2018-7600!" + '\n')
  if vuln_status[2]:
    print("[+] Possibly vulnerable to CVE-2018-7602!")
    if verbose == True:
      print("[+] See " + cve_2018_7602[-1] + " for more information.")
    if args.outfile:
      file.write("[+] Possibly vulnerable to CVE-2018-7602!" + '\n')
      file.write("[+] See " + cve_2018_7602[-1] + " for more information." + '\n')
  else:
    print("[-] Not vulnerable to CVE-2018-7602!")
    if args.outfile:
      file.write("[-] Not vulnerable to CVE-2018-7602!" + '\n')
  if args.outfile:
    file.write("==============================================================================================================================" + '\n\n')
  return vuln_status

####################################################################################################################

def get_version(target):
  version = None
  versionX = None
  user_agent = get_random_useragent()
  paths = [
      'CHANGELOG.txt',
      'core/CHANGELOG.txt',
      'includes/bootstrap.inc',
      'core/includes/bootstrap.inc',
      'includes/database.inc',
      'includes/database/database.inc',
      'core/includes/database.inc'
    ]

  print("[~] Checking the version of " + target)
  for path in paths:
    url = target + path
    if verbose == True:
      print("[~] Checking " + url)
    user_agent = get_random_useragent()
    headers = {'user-agent' : user_agent}

    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
      if verbose == True:
        print("[+] Page Found!!!")
      for line in r.text.splitlines():
        if "Drupal" in line:
          v = re.search(r"([\d][.][\d]?[.]?[\d])", line)
          if v is not None:
            if ("7." or "8." or "6.") not in v.group(0):
              versionX = v.group(0)
            else:
              version = v.group(0)
              break
      if version is not None:
        break

  if version is not None:
    if verbose == True:
      print("[+] Version: " + version + " Found")
    if args.outfile:
      file.write("[+] Version: " + version + " Found" + '\n')
      file.write("==============================================================================================================================" + '\n')

    return version
  elif versionX is not None:
    print("[!] Version: " + versionX + " Found")
    print("[!] This is more than likely WRONG!!!")
    return versionX
  else:
    while True:
      print("[-] Version: Not Detected. Possibly not a Drupal site...")
      print("[?] Would you like to continue? [y/n]")
      choice = input("[#] => ")
      if choice == "y":
        print("[?] What version do you want to test for? eg. 7.58")
        versionX = input("[#] => ")
        return versionX
      elif choice == "n":
        print("[0:)] Thank You For Using... Goodbye")
        raise SystemExit
      else:
        print("[!] INVALID SELECTION.... Select [y/n]")

####################################################################################################################

def prep_target(target):
  # Makes sure target url ends with /. If not append it
  if not (target.endswith("/")):
    target+=str("/")

  requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
  if verbose == True:
    print("[~] Verifying " + target + " is alive")

  try:
    user_agent = get_random_useragent()
    headers = {'user-agent' : user_agent}
    r = requests.get(target, headers=headers, verify=False)
  except:
    print("[!] " + target + " seems to be dead. Verify the URL provided...")
    raise SystemExit

  if verbose == True:
    print("[+] " + target + " seems to be alive")
  if args.outfile:
    file.write("[+] " + target + " seems to be alive" + '\n')
    file.write("==============================================================================================================================" + '\n')
  version = get_version(target)
  vuln_version = check_version(version)
  
  return version, vuln_version, target

####################################################################################################################

def main():
  print ()
  print ('+=================================================================================+')
  print ('|                                     iDrupal                                     |')
  print ('|                                    by IAmG0d                                    |')
  print ('+=================================================================================+\n')

## Grab target from list or range
  target = args.target
  version, vuln_version, target = prep_target(target)
  print("[0:)] Thank You For Using... Goodbye")
  raise SystemExit


####################################################################################################################

if __name__ == '__main__':
  parser = argparse.ArgumentParser( prog="drupa7-CVE-2018-7602.py",
    formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=50),
    description= '''
      This script is used to identify Drupal Installations within a network
    ''')

  parser.add_argument("target", help="URL of target Drupal site (ex: http://target.com/)")
  parser.add_argument("-o",  "--outfile",   default=False, action="store_true",  help="Save results to file")
  parser.add_argument("-v",  "--verbose",   default=False, action="store_true",  help="Increase output verbosity")
  args = parser.parse_args()

  if args.verbose:
    target = args.target
    verbose = True
  if args.outfile:
    file = open('log.out','a')
    file.write("==============================================================================================================================" + '\n')
    file.write("myDrupal.py" + '\n')
    file.write("==============================================================================================================================" + '\n')
  main()

####################################################################################################################
  
